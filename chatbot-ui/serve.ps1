$port = if ($env:PORT) { $env:PORT } else { "5500" }
$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add("http://localhost:$port/")
$listener.Start()
Write-Host "Server started on port $port"
Write-Host "Listening at http://localhost:$port/"
[Console]::Out.Flush()
while ($listener.IsListening) {
    $ctx = $listener.GetContext()
    $localPath = $ctx.Request.Url.LocalPath
    if ($localPath -eq '/' -or $localPath -eq '') {
        $localPath = '/index.html'
    }
    $filePath = "C:\Users\localadmin\Desktop\Projects\FinalALLAGENTS\chatbot-ui" + $localPath.Replace('/', '\')
    if (Test-Path $filePath) {
        $ext = [System.IO.Path]::GetExtension($filePath)
        $contentType = switch ($ext) {
            '.html' { 'text/html; charset=utf-8' }
            '.js'   { 'application/javascript' }
            '.css'  { 'text/css' }
            '.png'  { 'image/png' }
            default { 'text/plain' }
        }
        $bytes = [System.IO.File]::ReadAllBytes($filePath)
        $ctx.Response.ContentType = $contentType
        $ctx.Response.ContentLength64 = $bytes.Length
        $ctx.Response.OutputStream.Write($bytes, 0, $bytes.Length)
    } else {
        $ctx.Response.StatusCode = 404
        $msg = [System.Text.Encoding]::UTF8.GetBytes("404 Not Found")
        $ctx.Response.OutputStream.Write($msg, 0, $msg.Length)
    }
    $ctx.Response.Close()
}
