clear
echo "NAX Entertainment - v1.0.0 | Network Test and Log System"
echo "Starting download of required packages\n"
echo "Installing git"
pkg install git > /dev/null 2>&1
echo "Installing Termux-API"
pkg install termux-api > /dev/null 2>&1
echo "Installing Python3"
pkg install python3 > /dev/null 2>&1
echo "Installing Python3 PIP"
pkg install python3-pip > /dev/null 2>&1
echo "Starting NAX-NTLS | v1.0.0"
python3 ntls.py
