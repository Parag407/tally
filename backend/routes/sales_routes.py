"""
Sales Voucher Routes
Handles upload, preview, validation, and XML generation for sales vouchers.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from fastapi.responses import Response

from services.excel_parser import parse_file, dataframe_to_records
from services.smart_mapper import rule_based_map, ai_based_map
from services.validator import validate_sales
from services.xml_generator import generate_sales_xml

router = APIRouter()


@router.post("/upload")
async def upload_sales_file(
    file: UploadFile = File(...),
    use_ai: bool = Query(False, description="Use AI for column mapping"),
):
    """
    Upload an Excel/CSV file for sales voucher processing.
    Returns parsed data preview, column mapping, and validation errors.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    ext = file.filename.rsplit(".", 1)[-1].lower()
    if ext not in ("xlsx", "xls", "csv"):
        raise HTTPException(status_code=400, detail="Only .xlsx, .xls, and .csv files are accepted")

    try:
        contents = await file.read()
        df, columns = parse_file(contents, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

    if use_ai:
        mapping = await ai_based_map(columns, "sales")
    else:
        mapping = rule_based_map(columns, "sales")

    records = dataframe_to_records(df, mapping)
    cleaned, errors = validate_sales(records)

    preview_rows = []
    for idx, row in df.iterrows():
        preview = {"_row": int(idx) + 2}
        for col in columns:
            val = row[col]
            import pandas as pd
            preview[col] = None if pd.isna(val) else val
        preview_rows.append(preview)

    return {
        "filename": file.filename,
        "total_rows": len(df),
        "columns": columns,
        "mapping": mapping,
        "preview": preview_rows,
        "cleaned_data": cleaned,
        "errors": errors,
        "error_count": len(errors),
        "valid_count": sum(1 for r in cleaned if not r.get("has_errors")),
    }


@router.post("/generate-xml")
async def generate_sales_xml_endpoint(
    file: UploadFile = File(...),
    use_ai: bool = Query(False),
    auto_fixed: bool = Query(False),
    sales_ledger: str = Query("Sales Account", description="Sales ledger name in Tally"),
):
    """
    Generate Tally XML from uploaded sales file.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    try:
        contents = await file.read()
        df, columns = parse_file(contents, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

    if use_ai:
        mapping = await ai_based_map(columns, "sales")
    else:
        mapping = rule_based_map(columns, "sales")

    records = dataframe_to_records(df, mapping)
    cleaned, errors = validate_sales(records)

    if errors:
        critical_errors = [e for e in errors if e.get("is_critical", False)]
        if critical_errors or not auto_fixed:
            raise HTTPException(status_code=422, detail={
                "message": "Validation errors found. Fix errors before generating XML.",
                "errors": errors,
                "error_count": len(errors),
            })

    xml_content = generate_sales_xml(cleaned, sales_ledger=sales_ledger)

    return Response(
        content=xml_content,
        media_type="application/xml",
        headers={
            "Content-Disposition": f'attachment; filename="sales_voucher.xml"'
        },
    )


@router.post("/validate")
async def validate_sales_file(
    file: UploadFile = File(...),
    use_ai: bool = Query(False),
):
    """Validate sales file and return only errors."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    try:
        contents = await file.read()
        df, columns = parse_file(contents, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {str(e)}")

    if use_ai:
        mapping = await ai_based_map(columns, "sales")
    else:
        mapping = rule_based_map(columns, "sales")

    records = dataframe_to_records(df, mapping)
    cleaned, errors = validate_sales(records)

    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "error_count": len(errors),
        "total_rows": len(df),
        "valid_rows": sum(1 for r in cleaned if not r.get("has_errors")),
    }
