#! /bin/bash

DIRPATH=$1

CMD="/opt/homebrew-cask/Caskroom/libreoffice/5.1.3/LibreOffice.app/Contents/MacOS/soffice"

$CMD --headless --convert-to "csv:Text" $DIRPATH/* --outdir $DIRPATH
$CMD --headless --convert-to "csv" $DIRPATH/* --outdir $DIRPATH
$CMD --headless --convert-to "csv:Text - txt - csv (StarCalc):44,34,76,1,1/1" $DIRPATH/* --outdir $DIRPATH
