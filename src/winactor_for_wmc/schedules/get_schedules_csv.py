from winactor_for_wmc.common import get_departments
from winactor_for_wmc.common.client import WMCApiClient


def run(**kwargs):
    base_url = kwargs.get("base_url")
    token = kwargs.get("token")
    save_path = kwargs.get("save_path")

    raw_params = dict(kwargs.get("params") or {})

    # 所属名が来ている場合は、必要に応じて ID に変換
    departments_url = raw_params.get("departments_url") or base_url

    dn1 = _norm(raw_params.get("department_name1"))
    dn2 = _norm(raw_params.get("department_name2"))
    dn3 = _norm(raw_params.get("department_name3"))

    has_names = any(x is not None for x in (dn1, dn2, dn3))
    has_ids = any(
        raw_params.get(k) is not None
        for k in ("department1", "department2", "department3")
    )

    if has_names and not has_ids:
        dep_result = get_departments.get_departments(
            base_url=departments_url,
            token=token,
        )

        if hasattr(get_departments, "get_departments_ids_by_names_or_error"):
            d1_id, d2_id, d3_id = get_departments.get_departments_ids_by_names_or_error(
                dep_result,
                department_name1=dn1,
                department_name2=dn2,
                department_name3=dn3,
            )
        else:
            d1_id, d2_id, d3_id = get_departments.get_departments_ids_by_names(
                dep_result,
                department_name1=dn1,
                department_name2=dn2,
                department_name3=dn3,
            )
            if d1_id is None and d2_id is None and d3_id is None:
                raise ValueError(
                    "指定された所属が見つからないか一意に定まりません: "
                    f"department_name1={dn1}, department_name2={dn2}, department_name3={dn3}"
                )

        if d1_id is not None:
            raw_params["department1"] = d1_id
        if d2_id is not None:
            raw_params["department2"] = d2_id
        if d3_id is not None:
            raw_params["department3"] = d3_id

    # API に渡すキーを制限
    allowed = {
        "encoding",
        "updatedAtType",
        "updatedAtDate1",
        "updatedAtDate2",
        "department1",
        "department2",
        "department3",
    }
    params = {k: v for k, v in raw_params.items() if k in allowed}

    endpoint = "/schedules/csv"
    client = WMCApiClient(base_url, token)
    client.get_csv(endpoint, params=params, save_path=save_path)
    return


def _norm(x):
    if x is None:
        return None
    if isinstance(x, str):
        s = x.strip()
        return s if s else None
    return x
