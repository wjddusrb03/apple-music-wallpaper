Set fso = CreateObject("Scripting.FileSystemObject")
Set WshShell = CreateObject("WScript.Shell")
strPath = fso.GetParentFolderName(WScript.ScriptFullName)

' Check if first-time setup is needed
If fso.FileExists(strPath & "\python\python.exe") Then
    ' Already installed: run server silently (no CMD window)
    WshShell.Run """" & strPath & "\python\python.exe"" """ & strPath & "\server.py""", 0, False

    ' Launch Lively Wallpaper
    WScript.Sleep 1000
    WshShell.Run "explorer.exe ""shell:AppsFolder\12030rocksdanister.LivelyWallpaper_97hta09mmv6hy!App""", 0, False
Else
    ' First time: show CMD for setup progress
    WshShell.Run """" & strPath & "\start.bat""", 1, False
End If
