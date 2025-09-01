from winactor_for_wmc.common.client import WMCApiClient


def get_departments(**kwargs):
    """
    /departments を呼び出して所属一覧を取得する。
    引数はキーワードで受け取り、そのままクエリに反映する。
    """
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")
    idType = kwargs.get("idType")
    _id = kwargs.get("id")  # 'id' は組込みと被るので一旦 _id に
    department1 = kwargs.get("department1")
    department2 = kwargs.get("department2")
    department3 = kwargs.get("department3")
    page = kwargs.get("page")
    size = kwargs.get("size")

    endpoint = "/departments"

    # デフォルトで 10000 件取得
    if size is None:
        size = 10000

    params = {}
    if idType:
        params["idType"] = idType
    if _id:
        params["id"] = _id
    if department1:
        params["department1"] = department1
    if department2:
        params["department2"] = department2
    if department3:
        params["department3"] = department3
    if page is not None:
        params["page"] = page
    # size は常に付与
    params["size"] = size

    client = WMCApiClient(base_url, token)
    return client.get(endpoint, params=params)


def get_departments_ids_by_names(
    result,
    department_name1=None,
    department_name2=None,
    department_name3=None,
):
    """
    取得した所属一覧(result)から、部門名（1/2/3）で整合する行を見つけ、
    department1/2/3 のIDを返す。

    仕様（完全版）:
    - 空文字や空白のみは未指定(None)として扱う。
    - 同一の行で整合する候補を抽出してから判定する。
    - 指定階層がすべて埋まっていなくても、指定された範囲で一意に定まれば、
      その階層までの ID を返し、未指定の下位は None を返す。
    - 一意に定まらない、または一致行がない場合は (None, None, None) を返す。
    """
    items = result.get("items", []) or []

    # 入力値を正規化: 空白のみの文字列は None とみなす
    def norm_in(x):
        if x is None:
            return None
        if isinstance(x, str):
            s = x.strip()
            return s if s != "" else None
        return x

    # 取得データの比較用: 文字列なら strip して比較
    def norm_item(x):
        return x.strip() if isinstance(x, str) else x

    n1 = norm_in(department_name1)
    n2 = norm_in(department_name2)
    n3 = norm_in(department_name3)

    # 何も指定がなければ決めようがない
    if n1 is None and n2 is None and n3 is None:
        return None, None, None

    # 指定条件に一致する「同一行」候補を抽出
    candidates = [
        it
        for it in items
        if (n1 is None or norm_item(it.get("departmentName1")) == n1)
        and (n2 is None or norm_item(it.get("departmentName2")) == n2)
        and (n3 is None or norm_item(it.get("departmentName3")) == n3)
    ]

    if not candidates:
        return None, None, None

    # 3階層すべて指定 → 完全一致の先頭を採用
    if n1 is not None and n2 is not None and n3 is not None:
        row = candidates[0]
        return row.get("department1"), row.get("department2"), row.get("department3")

    # 親＋子 指定（孫未指定）→ (親, 子) の組み合わせが一意なら返す
    if n1 is not None and n2 is not None and n3 is None:
        pairs = {(it.get("department1"), it.get("department2")) for it in candidates}
        if len(pairs) == 1:
            d1, d2 = next(iter(pairs))
            return d1, d2, None
        return None, None, None

    # 親のみ 指定 → 親ID が一意なら親だけ返す
    if n1 is not None and n2 is None and n3 is None:
        parents = {it.get("department1") for it in candidates}
        if len(parents) == 1:
            return next(iter(parents)), None, None
        return None, None, None

    # 子のみ 指定 → 子ID が一意なら子だけ返す（親・孫は None）
    if n1 is None and n2 is not None and n3 is None:
        children = {it.get("department2") for it in candidates}
        if len(children) == 1:
            return None, next(iter(children)), None
        return None, None, None

    # 子＋孫 指定（親未指定）→ (子, 孫) が一意なら返す（親は None）
    if n1 is None and n2 is not None and n3 is not None:
        pairs = {(it.get("department2"), it.get("department3")) for it in candidates}
        if len(pairs) == 1:
            d2, d3 = next(iter(pairs))
            return None, d2, d3
        return None, None, None

    # 孫のみ 指定 → 孫ID が一意なら孫だけ返す
    if n1 is None and n2 is None and n3 is not None:
        grandchildren = {it.get("department3") for it in candidates}
        if len(grandchildren) == 1:
            return None, None, next(iter(grandchildren))
        return None, None, None

    # どれにも当てはまらない場合
    return None, None, None
