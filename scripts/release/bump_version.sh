#!/usr/bin/env bash

set -e

read -p "Enter current version: " OLD_VERSION
read -p "Enter new version    : " NEW_VERSION

echo "Bumping version from $OLD_VERSION to $NEW_VERSION..."

FILES=(
  .bumpversion.cfg
  docs/source/conf.py
  nucypher/__about__.py
)

SED_COMMAND="sed -i -e \"s/$OLD_VERSION/$NEW_VERSION/g\""

if [[ "$OSTYPE" == "darwin"* ]]; then
  # special case for mac that has slightly different usage for "-i" option
  SED_COMMAND="sed -i '' -e \"s/$OLD_VERSION/$NEW_VERSION/g\""
fi

for f in "${FILES[@]}"; do
  eval "$SED_COMMAND $f"
done

echo
echo "Showing diff..."
git diff ${FILES[*]}

echo
read -p "Commit diff? (type y or Y): " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo
    echo "Committing files..."
    git add ${FILES[*]}
    # git commit -m "Bump version: $OLD_VERSION → $NEW_VERSION"
fi

echo
echo "Done!"
