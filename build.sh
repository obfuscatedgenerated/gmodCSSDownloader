# set seed to a known repeatable integer value
PYTHONHASHSEED=1
export PYTHONHASHSEED
SOURCE_DATE_EPOCH=$(git log -1 --pretty=%ct)
export SOURCE_DATE_EPOCH
# create one-file build as myscript
pyinstaller ./spec/gmodCSSDownloader.spec
# make checksum
cksum dist/gmodCSSDownloader | awk '{print $1}' > dist/checksum.txt
# let Python be unpredictable again
unset PYTHONHASHSEED
unset SOURCE_DATE_EPOCH