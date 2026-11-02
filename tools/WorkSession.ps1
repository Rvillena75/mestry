param(
    [Parameter(Mandatory = $true)][string]$Repo,
    [ValidateSet('start', 'finish', 'receive', 'check')][string]$Action = 'check',
    [string]$Distribution,
    [Parameter(ValueFromRemainingArguments = $true)][string[]]$SessionArguments
)
$ErrorActionPreference = 'Stop'
$wslArguments = @()
if ($Distribution) { $wslArguments += @('--distribution', $Distribution) }
$wslArguments += @('--cd', $Repo, '--exec', 'sh', 'tools/work-session.sh', $Action)
$wslArguments += $SessionArguments
& wsl.exe @wslArguments
exit $LASTEXITCODE
