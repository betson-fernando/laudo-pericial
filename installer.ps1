$null = New-Item -Path "C:\temp" -ItemType "directory" -Force

<#
"Realizando download de Python..."
try{
	$result=Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.13.2/python-3.13.2-amd64.exe' -OutFile 'C:\temp\python.exe'
}
catch{
	"Erro em baixar o executável python."
	Remove-Item -Path "C:\temp" -Force -Recurse
	exit
}
"Realizando a instalação de Python..."
C:\temp\python.exe

"Realizando download de TexMaker..."
try{
	Invoke-WebRequest -Uri 'https://www.xm1math.net/texmaker/assets/files/Texmaker_6.0.0_Win_x64.msi' -OutFile 'C:\temp\texmaker.msi'
}
catch{
	"Erro em baixar o executável texmaker."
	Remove-Item -Path "C:\temp" -Force -Recurse
	exit
}
"Realizando a instalação de Texmaker..."	
C:\temp\texmaker.msi


"Realizando download de MikTex..."
try{
	Invoke-WebRequest -Uri 'https://miktex.org/download/ctan/systems/win32/miktex/setup/windows-x64/miktexsetup-5.5.0+1763023-x64.zip' -OutFile 'C:\temp\miktex.zip'
}
catch{
	"Erro em baixar o executável Miktex."
	Remove-Item -Path "C:\temp" -Force -Recurse
	exit
}
"Realizando a instalação de MikTex..."
Expand-Archive -Path C:\temp\miktex.zip -DestinationPath C:\temp
C:\temp\miktexsetup_standalone.exe --quiet --local-package-repository=C:\temp\miktex --package-set=basic download
C:\temp\miktexsetup_standalone.exe --quiet --local-package-repository=C:\temp\miktex --package-set=basic install



$configs = Get-Content "texmaker_conf.ini"
$miktex_path = where.exe MikTex
$configs = $configs -replace 'Tools\\Latex="[\S ]+', "Tools\Latex=""\""$($miktex_path)\"" -interaction=nonstopmode %.tex"""
"Espere até a finalização da instalação do Miktex antes de continuar."
pause

mpm --require=@".\packages.txt"

pip install --upgrade python


#>

py -m pip install --upgrade pip
pip install pandas, monthdelta, load_dotenv, requests, openpyxl

# $path = pip show pip | Select-String "^Location" | ForEach-Object { ($_ -split ":\s*(?![\/\\])")[1]}
pause
Remove-Item -Path "C:\temp" -Force -Recurse