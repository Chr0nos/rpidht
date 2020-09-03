install:
	cp ./dht.service /etc/systemd/system/
	sudo systemctl enable dht.service
