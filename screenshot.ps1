param (
    [Parameter(Mandatory = $true)]
    [ValidateSet("light", "dark")]
    [string]$theme
)

$version = (Get-Content torf_gui/version.py | Select-String -Pattern "__version__").ToString().Split(" ")[2].Trim('"')

# Start the Python script and keep a reference to the spawned process to close it later
$originalProcess = Start-Process python -ArgumentList "torf_gui/gui.py" -WindowStyle Hidden -PassThru

# Wait for the new process to start
Start-Sleep -Seconds 5

# Get the new Python process
$newProcess = Get-Process -Name python | Where-Object { $_.Id -ne $originalProcess.Id }

# Capture the window screenshot
Add-Type -TypeDefinition @"
using System;
using System.Drawing;
using System.Windows.Forms;
using System.Runtime.InteropServices;

[StructLayout(LayoutKind.Sequential)]
public struct RECT {
    public int Left;
    public int Top;
    public int Right;
    public int Bottom;
}

public class ScreenCapture {
    [DllImport("user32.dll")]
    public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);

    [DllImport("user32.dll")]
    public static extern bool GetClientRect(IntPtr hWnd, out RECT lpRect);

    [DllImport("user32.dll")]
    public static extern bool ClientToScreen(IntPtr hWnd, ref Point lpPoint);

    public Image CaptureWindow(string windowTitle) {
        IntPtr handle = FindWindow(null, windowTitle);
        if (handle == IntPtr.Zero) {
            throw new ArgumentException(String.Format("Window with title '{0}' not found.", windowTitle));
        }

        RECT rect;
        GetClientRect(handle, out rect);
        var topLeft = new Point(rect.Left, rect.Top);
        var bottomRight = new Point(rect.Right, rect.Bottom);
        ClientToScreen(handle, ref topLeft);
        ClientToScreen(handle, ref bottomRight);
        return CaptureArea(new Rectangle(topLeft.X, topLeft.Y, bottomRight.X - topLeft.X, bottomRight.Y - topLeft.Y));
    }

    public Image CaptureArea(Rectangle area) {
        var bitmap = new Bitmap(area.Width, area.Height);
        using (var graphics = Graphics.FromImage(bitmap)) {
            graphics.CopyFromScreen(area.Left, area.Top, 0, 0, area.Size);
        }
        return bitmap;
    }
}
"@ -ReferencedAssemblies System.Drawing, System.Windows.Forms

$screenCapture = New-Object ScreenCapture
$bitmap = $screenCapture.CaptureWindow("torf-gui $version")
$bitmap.Save("screenshot-$theme.png", [System.Drawing.Imaging.ImageFormat]::Png)

# Close the Python script
$newProcess.Kill()