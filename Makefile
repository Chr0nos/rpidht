install:
	sudo cp ./dht.service /etc/systemd/system/
	sudo systemctl enable dht.service

uninstall:
	sudo systemctl disable dht.service
	sudo systemctl stop dht.service || true
	sudo rm -f /etc/systemd/system/dht.service
