from datapackage import Package
def p(): 
	package = Package('https://datahub.io/core/world-cities/datapackage.json')

	# print processed tabular data (if exists any)
	for resource in package.resources:
		if resource.descriptor['datahub']['type'] == 'derived/csv':
			resource = resource.read()
			for r in resource:
				print(r[0] + " " + r[1])

if __name__ == '__main__':
	p()