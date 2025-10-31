from time import sleep

from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")
    winactor_id = kwargs.get("winactor_id")

    client = WMCApiClient(base_url, token)

    # 1) WinActorの割当停止（exclude）
    #    PUT /winactors/{id}/exclude
    client.put(f"/winactors/{winactor_id}/exclude")

    # 2) 反映待ち：status が exclude になるまで短時間ポーリング
    try:
        for _ in range(20):  # 最大約10秒
            info = client.get(f"/winactors/{winactor_id}")
            if isinstance(info, dict) and info.get("status") == "exclude":
                break
            sleep(0.5)
    except Exception:
        # 取得失敗時は続行（exclude 要求は送信済み）
        pass

    # 3) WinActorの削除
    #    DELETE /winactors/{id}
    response = client.delete(f"/winactors/{winactor_id}")
    return response
