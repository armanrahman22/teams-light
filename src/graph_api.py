import logging
import json
import msal
import requests
import atexit
import os.path

# Globals
TENANT_ID = "72f988bf-86f1-41af-91ab-2d7cd011db47"
CLIENT_ID = "c3d56aa5-7307-452b-bed2-d5a8702fcc15"
AUTHORITY = "https://login.microsoftonline.com/" + TENANT_ID
ENDPOINT = "https://graph.microsoft.com/beta"

SCOPES = ["User.Read"]

cache = msal.SerializableTokenCache()

if os.path.exists("token_cache.bin"):
    cache.deserialize(open("token_cache.bin", "r").read())

atexit.register(
    lambda: open("token_cache.bin", "w").write(cache.serialize())
    if cache.has_state_changed
    else None
)

app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY, token_cache=cache)

accounts = app.get_accounts()
result = None
if len(accounts) > 0:
    result = app.acquire_token_silent(SCOPES, account=accounts[0])

if result is None:
    flow = app.initiate_device_flow(scopes=SCOPES)
    if "user_code" not in flow:
        raise Exception("Failed to create device flow")

    print(flow["message"])

    result = app.acquire_token_by_device_flow(flow)

if "access_token" in result:
    test = requests.get(
        f"{ENDPOINT}/me", headers={"Authorization": "Bearer " + result["access_token"]}
    )
    test.raise_for_status()
else:
    raise Exception("no access token in result")


def me():
    return query(ENDPOINT, "me", {"Authorization": "Bearer " + result["access_token"]})


def get_presence():
    return query(
        ENDPOINT,
        "me/presence",
        {
            "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJub25jZSI6IldiQ3p6c0ZWRGotRmZnemZtWW9MWlg5TnR5dnVMdHNqLUZTNF82T1E1U2siLCJhbGciOiJSUzI1NiIsIng1dCI6ImtnMkxZczJUMENUaklmajRydDZKSXluZW4zOCIsImtpZCI6ImtnMkxZczJUMENUaklmajRydDZKSXluZW4zOCJ9.eyJhdWQiOiIwMDAwMDAwMy0wMDAwLTAwMDAtYzAwMC0wMDAwMDAwMDAwMDAiLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC83MmY5ODhiZi04NmYxLTQxYWYtOTFhYi0yZDdjZDAxMWRiNDcvIiwiaWF0IjoxNjA1MTI1MjgyLCJuYmYiOjE2MDUxMjUyODIsImV4cCI6MTYwNTEyOTE4MiwiYWNjdCI6MCwiYWNyIjoiMSIsImFjcnMiOlsidXJuOnVzZXI6cmVnaXN0ZXJzZWN1cml0eWluZm8iLCJ1cm46bWljcm9zb2Z0OnJlcTIiLCJ1cm46bWljcm9zb2Z0OnJlcTMiXSwiYWlvIjoiQWFRQVcvOFJBQUFBSk1HTzRROFdKdnEzSlNUQ1cvVjVLSHVjMmVmckFDMmQxUnZXYldFQXZ4aGxuWkxSZmdjUGR3bWJ6MDh6VWtnZUZZMjRzNUhPbXQySkFPUEY2aWRBZnQ4WjZ3eDV0OG5QTGZaZmdMbU1xbTJNQitmeDJjVXFrZWFnamp0WUdTMC9lcCtVWm5wVGpJRFZUV1hqbVhVOE15TnQweDd5QVhtYkdzR3RjYS9Ca2hZUTlnekVvM0tidVh4Z1dtNTJHZEh6UnFQaXBCR2ovbnY0NmllUSsrL2t2dz09IiwiYW1yIjpbInB3ZCIsInJzYSIsIm1mYSJdLCJhcHBfZGlzcGxheW5hbWUiOiJHcmFwaCBleHBsb3JlciAob2ZmaWNpYWwgc2l0ZSkiLCJhcHBpZCI6ImRlOGJjOGI1LWQ5ZjktNDhiMS1hOGFkLWI3NDhkYTcyNTA2NCIsImFwcGlkYWNyIjoiMCIsImRldmljZWlkIjoiMGIyZDEzODgtNTNlZS00OTA3LWFjMGUtOWUxOWJhYzk1Zjk4IiwiZmFtaWx5X25hbWUiOiJSYWhtYW4iLCJnaXZlbl9uYW1lIjoiQXJtYW4iLCJpZHR5cCI6InVzZXIiLCJpcGFkZHIiOiI5OC4xNjQuNzEuMTE3IiwibmFtZSI6IkFybWFuIFJhaG1hbiIsIm9pZCI6Ijk4YWM2MGNlLWI0MzQtNDE1Zi1hNTJkLTExNTQyYzFjMTc3ZiIsIm9ucHJlbV9zaWQiOiJTLTEtNS0yMS0xMjQ1MjUwOTUtNzA4MjU5NjM3LTE1NDMxMTkwMjEtMTc1NTkyMiIsInBsYXRmIjoiMyIsInB1aWQiOiIxMDAzMDAwMEEzRUYyNUMzIiwicmgiOiIwLkFSb0F2NGo1Y3ZHR3IwR1JxeTE4MEJIYlI3WElpOTc1MmJGSXFLMjNTTnB5VUdRYUFPSS4iLCJzY3AiOiJDYWxlbmRhcnMuUmVhZFdyaXRlIENvbnRhY3RzLlJlYWRXcml0ZSBEZXZpY2VNYW5hZ2VtZW50QXBwcy5SZWFkV3JpdGUuQWxsIERldmljZU1hbmFnZW1lbnRDb25maWd1cmF0aW9uLlJlYWQuQWxsIERldmljZU1hbmFnZW1lbnRDb25maWd1cmF0aW9uLlJlYWRXcml0ZS5BbGwgRGV2aWNlTWFuYWdlbWVudE1hbmFnZWREZXZpY2VzLlByaXZpbGVnZWRPcGVyYXRpb25zLkFsbCBEZXZpY2VNYW5hZ2VtZW50TWFuYWdlZERldmljZXMuUmVhZC5BbGwgRGV2aWNlTWFuYWdlbWVudE1hbmFnZWREZXZpY2VzLlJlYWRXcml0ZS5BbGwgRGV2aWNlTWFuYWdlbWVudFJCQUMuUmVhZC5BbGwgRGV2aWNlTWFuYWdlbWVudFJCQUMuUmVhZFdyaXRlLkFsbCBEZXZpY2VNYW5hZ2VtZW50U2VydmljZUNvbmZpZy5SZWFkLkFsbCBEZXZpY2VNYW5hZ2VtZW50U2VydmljZUNvbmZpZy5SZWFkV3JpdGUuQWxsIERpcmVjdG9yeS5BY2Nlc3NBc1VzZXIuQWxsIERpcmVjdG9yeS5SZWFkV3JpdGUuQWxsIEZpbGVzLlJlYWRXcml0ZS5BbGwgR3JvdXAuUmVhZFdyaXRlLkFsbCBJZGVudGl0eVJpc2tFdmVudC5SZWFkLkFsbCBNYWlsLlJlYWRXcml0ZSBNYWlsYm94U2V0dGluZ3MuUmVhZFdyaXRlIE5vdGVzLlJlYWRXcml0ZS5BbGwgb3BlbmlkIFBlb3BsZS5SZWFkIFByZXNlbmNlLlJlYWQgUHJlc2VuY2UuUmVhZC5BbGwgcHJvZmlsZSBSZXBvcnRzLlJlYWQuQWxsIFNpdGVzLlJlYWRXcml0ZS5BbGwgVGFza3MuUmVhZFdyaXRlIFVzZXIuUmVhZCBVc2VyLlJlYWRCYXNpYy5BbGwgVXNlci5SZWFkV3JpdGUgVXNlci5SZWFkV3JpdGUuQWxsIGVtYWlsIiwic2lnbmluX3N0YXRlIjpbImR2Y19tbmdkIiwiZHZjX2NtcCIsImttc2kiXSwic3ViIjoiejh5UkdaOHBNV0dBVW9xdTZGbnFSYlZUS3NWYW02QXlPWEpXWFlQRWVTYyIsInRlbmFudF9yZWdpb25fc2NvcGUiOiJXVyIsInRpZCI6IjcyZjk4OGJmLTg2ZjEtNDFhZi05MWFiLTJkN2NkMDExZGI0NyIsInVuaXF1ZV9uYW1lIjoiYXJyYWhtQG1pY3Jvc29mdC5jb20iLCJ1cG4iOiJhcnJhaG1AbWljcm9zb2Z0LmNvbSIsInV0aSI6IlZoZEYwc1JSd2stSTFXUkdkMmE1QWciLCJ2ZXIiOiIxLjAiLCJ3aWRzIjpbImI3OWZiZjRkLTNlZjktNDY4OS04MTQzLTc2YjE5NGU4NTUwOSJdLCJ4bXNfc3QiOnsic3ViIjoidTFaT0c3aU5ncjhwR1J1MWNWVXFhc0hRVktNc2Rxa1NmTTlWRzdlQnBBVSJ9LCJ4bXNfdGNkdCI6MTI4OTI0MTU0N30.S16DD6UlnLTf7VW6Ovpa-IEIgNQapgwmC3mKsycJsM08XLMkbJwDkZWJFGQMz6pocuk2wLWpo1-bgxD5TcQD1U5zAB3Dw50QDa4uxyU0W40pQsqlnThN4bb6xUWG_TcOw4I2eBeb4xzVHkjxtslmMWNPpSrgx2hzGB6fZYQUjny47Hmk-y1U69ok4HcrgJDHywyhUzC90-3lH-TBjdcLC9OiT_ES0ZzuwIKFq1uKVRbvyj6wrwqHOZf9yFOxSCahYEKnZ39UgWNpeFS8UYEVRlJZNbfiU_TuKjPni_4gtDCV0mz_wIhm_5658DhrhRuNhNGs7mlSyxfPSbuUb_ayKg"
        },
    )["availability"]


def query(base_url, end_point, headers):
    result = requests.get(f"{base_url}/{end_point}", headers=headers)
    result.raise_for_status()
    return result.json()
