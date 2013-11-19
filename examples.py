import time

def log(filename):
	def wrapper(func):
		f = open(filename, "w")
		f.write("start")
		try:
			func()
		except Exception as e:
			f.write("error"+str(e))
		else:
			f.write("stop")
		finally:
			f.close()

		#with open(filename) as f:
		#	f.write("start")
		#	func()
		#	f.write("stop")

	return wrapper

dec = log("file1.txt")

@dec
def longOperation1():
	return 1+1


@log("file2.txt")
def longOperation2():
	return 1-1




#timeOp1 = timer(longOperation1)
#timeOp2 = timer(longOperation2)

#longOperation1()



#python
#flask
#html

#http

#bootstrap
#SQL
#sqlite

from flask import Flask
app = Flask(__name__)

#@app.route("/")



def xxx():
    return "<h1>Hello World2!</h1>"

dec = app.route("/asdf")
hello = dec(xxx)

if __name__ == "__main__":
    app.run()
