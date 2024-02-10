param (
    [Parameter(Mandatory = $true)]
    [ValidateSet("light", "dark")]
    [string]$theme
)

# Debug print the theme
Write-Host "Theme: $theme"

$version = (Get-Content torf_gui/version.py | Select-String -Pattern "__version__").ToString().Split(" ")[2].Trim('"')

# Print the version

Write-Host "Version: $version"

# Start the Python script
python "torf_gui/gui.py" &

Write-Host "Waiting for the process to start..."


# Wait for the new process to start
Start-Sleep -Seconds 5

# Get the new Python process
$newProcess = Get-Process -Name python | Where-Object { $_.Id -ne $originalProcess.Id }

# Debug print running processes
Write-Host "Running processes:"
Get-Process | ForEach-Object { Write-Host $_.Name }

# Debug print the process ID
Write-Host "Process ID: $($newProcess.Id)"

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

# Capture the window screenshot

Write-Host "Capturing the window screenshot..."

$screenCapture = New-Object ScreenCapture
Write-Host "Test 1"
$bitmap = $screenCapture.CaptureWindow("torf-gui $version")
Write-Host "Test 2"
$bitmap.Save("screenshot-$theme.png", [System.Drawing.Imaging.ImageFormat]::Png)
Write-Host "Test 3"

# Close the Python script
# $newProcess.Kill()