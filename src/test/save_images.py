from ppadb.client import Client as AdbClient

if __name__ == "__main__":
	client = AdbClient(host="127.0.0.1", port=5037)
	device = client.devices()[0]

	i = 0
	while True:
		x = input()
		result = device.screencap()
		print("index " + str(i))
		with open("images/test" + str(i) + ".png", "wb") as fp:
			fp.write(result)
		i += 1
