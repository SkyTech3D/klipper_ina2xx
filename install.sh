#!/bin/bash
repo=klipper_ina2xx
repo_path="$(cd "$(dirname "$0")" && pwd)"

# Exit if root
if [ "$(id -u)" = "0" ]; then
    echo "Script must run from non-root !!!"
    exit
fi

module_name=ina226.py
module_path=~/klipper/klippy/extras/

# Linking
ln -sf "$repo_path/$module_name" $module_path

blk_path=~/printer_data/config/moonraker.conf
# Include update block in moonraker.conf
if [ -f "$blk_path" ]; then
    if ! grep -q "^\[update_manager $repo\]$" "$blk_path"; then
        read -p " Do you want to install updater? (y/n): " answer
        if [ "$answer" != "${answer#[Yy]}" ]; then
          sudo service moonraker stop
          sed -i "\$a \ " "$blk_path"
          sed -i "\$a [update_manager $repo]" "$blk_path"
          sed -i "\$a type: git_repo" "$blk_path"
          sed -i "\$a path: $repo_path" "$blk_path"
          sed -i "\$a origin: https://github.com/SkyTech3D/$repo.git" "$blk_path"
          sed -i "\$a primary_branch: main" "$blk_path"
          sed -i "\$a managed_services: klipper" "$blk_path"
          # echo "Including [update_manager] to $blk_path successfully complete"
          sudo service moonraker start
        else
          echo "Installing updater aborted"
        fi
    else
        echo "Including [update_manager] aborted, [update_manager] already exists in $blk_path"
    fi
fi