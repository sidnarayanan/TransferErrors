parent_path=/afs/cern.ch/user/s/snarayan/TransferErrors/
www_path=/afs/cern.ch/user/s/snarayan/www/TransferErrors/
cd $parent_path
source ./setup.sh
#echo "pythonpath:" $PYTHONPATH
python $parent_path/bin/run.py --refresh     # does all the API calls and puts stuff in stuck.pkl
python $parent_path/bin/write.py    # parses stuck.pkl into a HTML table
mkdir -p $www_path
cp -f -R $WEBDIR/d3 $www_path
cp -f -R $WEBDIR/data.csv $www_path
cp -f -R $WEBDIR/display.html $www_path
cp -f -R $WEBDIR/style.css $www_path
cp -f -R $WEBDIR/table.html $www_path
cp -f -R $WEBDIR/*.json $www_path
