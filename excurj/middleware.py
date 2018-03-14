class AMPMiddleware:

	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		response = self.get_response(request)
		response['Access-Control-Allow-Origin'] = "*"
		response['AMP-Redirect-To'] = "https://www.excurj.com"
		response['Access-Control-Allow-Methods'] = "POST, GET, OPTIONS"
		response['Access-Control-Allow-Headers'] = "Content-Type, Content-Length,Accept-Encoding, X-CSRF-Token"
		response['Access-Control-Expose-Headers'] = "AMP-Redirect-To,AMP-Access-Control-Allow-Source-Origin"
		response['AMP-Access-Control-Allow-Source-Origin'] = "http://localhost:8000, https://www.excurj.com"
		response['Access-Control-Allow-Credentials'] = "true"
		return response