#!/bin/bash

version=0.5

[[ -d build ]] && rm -r build
[[ -d dist ]] && rm -r dist

if [[ "`uname`" =~ "MINGW64" ]]; then
  [[ -f pyi-buygame-win.spec ]] && rm pyi-buygame-win.spec 
  [[ -f buygame-${version}.exe ]] && rm buygame-${version}.exe

  pyi-makespec.exe -w -F --paths venv/Lib/site-packages --paths gui --path gui/login --path gui/survey --path gui/gui_common --paths common --add-data "gui\tiles;gui\tiles" buygame.py -n pyi-buygame-win

  pyinstaller --clean ./pyi-buygame-win.spec

  [[ -d dist ]] && mv dist/pyi-buygame-win.exe buygame-${version}.exe
  echo "Buygame binary buygame-${version}.exe successfully created"

elif [[ "`uname`" =~ "Darwin" ]]; then
#  [[ -f pyi-buygame-mac.spec ]] && rm pyi-buygame-mac.spec 
  [[ -d buygame-${version}-mac.app ]] && rm -r buygame-${version}-mac.app
  [[ `which create-dmg` =~ 'not found' ]] && brew install create-dmg

  pyi-makespec -w -F --paths venv/Lib/site-packages --paths gui --path gui/login --path gui/survey --path gui/gui_common --paths common --add-data "gui/tiles:gui/tiles" buygame.py \
    --icon gui/tiles/bentley-logo.jpg \
    --windowed --onefile -n pyi-buygame-mac

  pyinstaller --clean ./pyi-buygame-mac.spec

  echo "Buygame binary buygame-${version}-mac.app successfully created"
  # [[ -d dist ]] && mv dist/pyi-buygame-mac.app buygame-${version}-mac.app
  

  mkdir -p dist/dmg
  rm -rf dist/dmg/*

  cp -r "dist/pyi-buygame-mac.app" dist/dmg

  [[ -f dist/buygame.dmg ]] && rm dist/buygame.dmg

  create-dmg \
     --volname "Buygame" \
     --volicon "gui/tiles/bentley-logo.jpg" \
     --window-pos 200 120 \
     --window-size 600 300 \
     --icon-size 100 \
     --icon "pyi-buygame-mac.app" 175 120 \
     --hide-extension "pyi-buygame-mac.app" \
     --app-drop-link 425 120 \
     "dist/buygame.dmg" \
     "dist/dmg/"
 
fi


