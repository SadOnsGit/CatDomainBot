import requests

from bot_create import DYNADOT_API_KEY, DYNADOT_API_URL


async def search_domain(domain) -> dict:
    params = {
        "key": DYNADOT_API_KEY,
        "command": 'search',
        "domain0": domain,
        "show_price": "1",
        "currency": "EUR"
    }
    try:
        r = requests.get(DYNADOT_API_URL, params=params, timeout=18)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


async def register_domain(ns, domain, years):
    params = {
        "key": DYNADOT_API_KEY,
        "command": 'register',
        "domain": domain,
        "currency": "EUR",
        "duration": str(years)
    }
    if ns:
        for i, ns in enumerate(ns):
            params[f"ns{i}"] = ns
    try:
        r = requests.get(DYNADOT_API_URL, params=params, timeout=18)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


async def get_domain_nameservers(domain_name: str) -> Optional[List[str]]:
    """
    Запрашивает текущие NS-сервера домена через API.
    Возвращает список NS или None в случае ошибки/не найден.
    """
    params = {
        "key": DYNADOT_API_KEY,
        "command": "get_dns",
        "domain": domain_name,
    }

    try:
        r = requests.get(DYNADOT_API_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        status = data.get("GetDnsResponse", {}).get("Status")
        if status != "success":
            print(f"Ошибка API: {data.get('GetDnsResponse', {}).get('Message')}")
            return None

        settings = (
            data.get("GetDnsResponse", {})
               .get("GetDns", {})
               .get("NameServerSettings", {})
        )
        ns_list = settings.get("NameServers")
        return [ns['ServerName'] for ns in ns_list]

    except Exception as e:
        print(f"Ошибка при запросе NS для {domain_name}: {e}")
        return None


async def change_domain_nameservers(
    domain_name: str,
    new_ns: List[str],
    timeout: int = 15
) -> Tuple[bool, str]:
    """
    Изменяет NS-сервера домена через API.
    """
    if not new_ns:
        return False, "Список NS пустой"

    if len(new_ns) > 13:
        return False, "Максимум 13 NS-серверов"

    params = {
        "key": DYNADOT_API_KEY,
        "command": "set_ns",
        "domain": domain_name,
    }

    for i, ns in enumerate(new_ns):
        params[f"ns{i}"] = ns.strip()

    try:
        r = requests.get(DYNADOT_API_URL, params=params, timeout=timeout)
        r.raise_for_status()
        
        data = r.json()
        
        status = data.get("SetNsResponse", {}).get("Status", "error")
        message = data.get("SetNsResponse", {}).get("Message", "Нет сообщения")

        if status == "success":
            return True, "NS успешно изменены"
        else:
            return False, f"Ошибка API: {message}"

    except requests.exceptions.RequestException as e:
        return False, f"Ошибка соединения: {str(e)}"
    except ValueError:
        return False, "Некорректный ответ от API"
    except Exception as e:
        return False, f"Неизвестная ошибка: {str(e)}"