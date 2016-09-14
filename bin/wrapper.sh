parent_path=/afs/cern.ch/user/j/jpulidom/transferteam/scripts/TransferErrors-master
cd $parent_path
source ./setup.sh
echo "pythonpath:" $PYTHONPATH
python $parent_path/bin/run.py --refresh     # does all the API calls and puts stuff in stuck.pkl
python $parent_path/bin/write.py    # parses stuck.pkl into a HTML table
cp -f -R $WEBDIR/d3 /afs/cern.ch/user/j/jpulidom/www/
cp -f -R $WEBDIR/data.csv /afs/cern.ch/user/j/jpulidom/www/
cp -f -R $WEBDIR/display.html /afs/cern.ch/user/j/jpulidom/www/
cp -f -R $WEBDIR/style.css /afs/cern.ch/user/j/jpulidom/www/
cp -f -R $WEBDIR/table.html /afs/cern.ch/user/j/jpulidom/www/