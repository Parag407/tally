"""
Template Routes
Handles sample Excel template downloads for each voucher type.
"""
from fastapi import APIRouter
from fastapi.responses import Response

from services.template_generator import (
    create_bank_template,
    create_sales_template,
    create_purchase_template,
    create_debit_note_template,
    create_credit_note_template,
)

router = APIRouter()


@router.get("/bank")
async def download_bank_template():
    """Download sample Excel template for bank vouchers."""
    template_bytes = create_bank_template()
    return Response(
        content=template_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": 'attachment; filename="bank_template.xlsx"'
        },
    )


@router.get("/sales")
async def download_sales_template():
    """Download sample Excel template for sales vouchers."""
    template_bytes = create_sales_template()
    return Response(
        content=template_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": 'attachment; filename="sales_template.xlsx"'
        },
    )


@router.get("/purchase")
async def download_purchase_template():
    """Download sample Excel template for purchase vouchers."""
    template_bytes = create_purchase_template()
    return Response(
        content=template_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": 'attachment; filename="purchase_template.xlsx"'
        },
    )


@router.get("/debit-note")
async def download_debit_note_template():
    """Download sample Excel template for Debit Note vouchers."""
    template_bytes = create_debit_note_template()
    return Response(
        content=template_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": 'attachment; filename="debit_note_template.xlsx"'
        },
    )


@router.get("/credit-note")
async def download_credit_note_template():
    """Download sample Excel template for Credit Note vouchers."""
    template_bytes = create_credit_note_template()
    return Response(
        content=template_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": 'attachment; filename="credit_note_template.xlsx"'
        },
    )
