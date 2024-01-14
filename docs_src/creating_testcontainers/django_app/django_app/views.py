import os

from django.http import HttpRequest, JsonResponse


def hello_api(request: HttpRequest) -> JsonResponse:
    greet = os.getenv("GREET", "stranger")
    return JsonResponse({"message": f"Hello from Django, {greet}!"})


def healthcheck_api(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"status": "ok"})
