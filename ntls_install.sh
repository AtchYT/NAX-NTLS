clear
echo "NAX Entertainment - v1.0.0 | Network Test and Log System"
echo "Starting download of required packages"
echo "Installing Termux-API"
pkg install termux-api > /dev/null 2>&1
echo "Installing Termux-API Battery and Telephone Status"
pkg install termux-telephony-deviceinfo > /dev/null 2>&1
pkg install termux-battery-status > /dev/null 2>&1
echo "Installing Python3"
pkg install python3 > /dev/null 2>&1
echo "Installing Python3 PIP"
pkg install python3-pip > /dev/null 2>&1
echo "Installing Python dependencies (pyfiglet and requests)"
pip install pyfiglet requests
echo "Installing Curl"
pkg install curl > /dev/null 2>&1
echo "Starting NAX-NTLS | v1.0.0"
python3 ntls.py
cd
