# winactor_for_wmc/common/get_departments.py
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

    変更点（エラー化のための厳格運用をデフォルト化）:
    - 入力正規化後に次を満たす場合は例外(ValueError)を送出します。
      * 子(department2)指定があるのに親(department1)未指定
      * 孫(department3)指定があるのに親/子未指定
      * 指定があるのに一致行が0件
      * 指定があるのに候補が複数で一意に定まらない
      * 指定した階層のIDが解決できない（例: 親名は指定したが親IDが取れない）
    - 3階層すべて未指定（空/空白含む）の場合のみ、(None, None, None) を返します。
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

    # 何も指定がなければ呼び出し側（未所属リセットなど）に委ねる
    if n1 is None and n2 is None and n3 is None:
        return None, None, None

    # 運用ルールの事前チェック
    if n2 is not None and n1 is None:
        raise ValueError("子所属を指定する場合は親所属も指定してください。")
    if n3 is not None and (n1 is None or n2 is None):
        raise ValueError("孫所属を指定する場合は親所属と子所属も指定してください。")

    # 指定条件に一致する「同一行」候補を抽出
    candidates = [
        it
        for it in items
        if (n1 is None or norm_item(it.get("departmentName1")) == n1)
        and (n2 is None or norm_item(it.get("departmentName2")) == n2)
        and (n3 is None or norm_item(it.get("departmentName3")) == n3)
    ]

    # 一致行ゼロならエラー
    if not candidates:
        raise ValueError(
            "指定された所属が見つかりません: "
            f"department_name1={n1}, department_name2={n2}, department_name3={n3}"
        )

    # 3階層すべて指定 → 完全一致の先頭を採用（候補が複数でもIDは同一想定、異なるなら後続チェックで弾く）
    if n1 is not None and n2 is not None and n3 is not None:
        row = candidates[0]
        d1, d2, d3 = (
            row.get("department1"),
            row.get("department2"),
            row.get("department3"),
        )
        # 念のため整合性確認（候補群でIDが食い違えば曖昧とみなす）
        if any(
            (it.get("department1"), it.get("department2"), it.get("department3"))
            != (d1, d2, d3)
            for it in candidates
        ):
            raise ValueError(
                "指定された所属が一意に定まりません（親+子+孫）: "
                f"department_name1={n1}, department_name2={n2}, department_name3={n3}"
            )
        return d1, d2, d3

    # 親＋子 指定（孫未指定）→ (親, 子) の組み合わせが一意であることを要求
    if n1 is not None and n2 is not None and n3 is None:
        pairs = {(it.get("department1"), it.get("department2")) for it in candidates}
        if len(pairs) != 1:
            raise ValueError(
                "指定された所属が一意に定まりません（親+子）: "
                f"department_name1={n1}, department_name2={n2}"
            )
        d1, d2 = next(iter(pairs))
        # 安全のため None チェック
        if d1 is None:
            raise ValueError(f"親所属が解決できません: department_name1={n1}")
        if d2 is None:
            raise ValueError(
                f"子所属が解決できません: department_name2={n2}（親: {n1}）"
            )
        return d1, d2, None

    # 親のみ 指定 → 親ID が一意であることを要求
    if n1 is not None and n2 is None and n3 is None:
        parents = {it.get("department1") for it in candidates}
        if len(parents) != 1:
            raise ValueError(
                "指定された所属が一意に定まりません（親のみ）: "
                f"department_name1={n1}"
            )
        d1 = next(iter(parents))
        if d1 is None:
            raise ValueError(f"親所属が解決できません: department_name1={n1}")
        return d1, None, None

    # 子のみ 指定（親未指定）は上の事前チェックでエラー済み

    # 子＋孫 指定（親未指定）は上の事前チェックでエラー済み

    # 孫のみ 指定（親・子未指定）は上の事前チェックでエラー済みだが、
    # 念のため既存分岐も厳格化（残しておく）
    if n1 is None and n2 is None and n3 is not None:  # pragma: no cover
        grandchildren = {it.get("department3") for it in candidates}  # pragma: no cover
        if len(grandchildren) != 1:  # pragma: no cover
            raise ValueError(  # pragma: no cover
                "指定された所属が一意に定まりません（孫のみ）: "
                f"department_name3={n3}"
            )
        d3 = next(iter(grandchildren))  # pragma: no cover
        if d3 is None:  # pragma: no cover
            raise ValueError(  # pragma: no cover
                f"孫所属が解決できません: department_name3={n3}"
            )
        return None, None, d3  # pragma: no cover

    # どれにも当てはまらない場合（理論上来ない）
    raise ValueError(
        "所属の判定に失敗しました（不正な入力の組み合わせ）"
    )  # pragma: no cover
