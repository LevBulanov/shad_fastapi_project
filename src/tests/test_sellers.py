import pytest
from fastapi import status
from sqlalchemy import select

from src.models.seller import Seller
from src.models.books import Book

API_V1_URL_PREFIX = "/api/v1/seller"


# CREATE SELLER
@pytest.mark.asyncio()
async def test_create_seller(async_client):

    data = {
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "email": "ivan@test.com",
        "password": "123456",
    }

    response = await async_client.post(f"{API_V1_URL_PREFIX}/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result = response.json()

    seller_id = result.pop("id", None)

    assert seller_id is not None

    assert result == {
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "email": "ivan@test.com",
    }

    # Проверяем что password не возвращается
    assert "password" not in response.json()


# GET SELLERS LIST
@pytest.mark.asyncio()
async def test_get_sellers(db_session, async_client):

    seller_1 = Seller(
        first_name="Ivan",
        last_name="Ivanov",
        email="ivan@test.com",
        password="hash",
    )

    seller_2 = Seller(
        first_name="Petr",
        last_name="Petrov",
        email="petr@test.com",
        password="hash",
    )

    db_session.add_all([seller_1, seller_2])
    await db_session.flush()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/")

    assert response.status_code == status.HTTP_200_OK

    sellers = response.json()["sellers"]

    assert len(sellers) == 2

    assert sellers == [
        {
            "id": seller_1.id,
            "first_name": "Ivan",
            "last_name": "Ivanov",
            "email": "ivan@test.com",
        },
        {
            "id": seller_2.id,
            "first_name": "Petr",
            "last_name": "Petrov",
            "email": "petr@test.com",
        },
    ]

    # Проверяем безопасность
    for seller in sellers:
        assert "password" not in seller


# GET SINGLE SELLER (AUTH REQUIRED)
@pytest.mark.asyncio()
async def test_get_single_seller(db_session, async_client, seller, auth_headers):

    book_1 = Book(
        title="Book 1",
        author="Author 1",
        year=2023,
        pages=100,
        seller_id=seller["id"],
    )

    book_2 = Book(
        title="Book 2",
        author="Author 2",
        year=2024,
        pages=200,
        seller_id=seller["id"],
    )

    db_session.add_all([book_1, book_2])
    await db_session.flush()

    response = await async_client.get(
        f"{API_V1_URL_PREFIX}/{seller['id']}",
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    data = response.json()

    assert data["id"] == seller["id"]
    assert data["email"] == seller["email"]

    assert "password" not in data

    assert len(data["books"]) == 2


# GET SINGLE SELLER WITHOUT TOKEN
@pytest.mark.asyncio()
async def test_get_single_seller_unauthorized(async_client):

    response = await async_client.get(f"{API_V1_URL_PREFIX}/1")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# UPDATE SELLER
@pytest.mark.asyncio()
async def test_update_seller(db_session, async_client, seller):

    data = {
        "first_name": "Updated",
        "last_name": "Seller",
        "email": seller["email"],
    }

    response = await async_client.put(
        f"{API_V1_URL_PREFIX}/{seller['id']}",
        json=data,
    )

    assert response.status_code == status.HTTP_200_OK

    await db_session.flush()

    updated = await db_session.get(Seller, seller["id"])

    assert updated.first_name == "Updated"
    assert updated.last_name == "Seller"


# DELETE SELLER
@pytest.mark.asyncio()
async def test_delete_seller(db_session, async_client, seller):

    book = Book(
        title="Book",
        author="Author",
        year=2024,
        pages=100,
        seller_id=seller["id"],
    )

    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{seller['id']}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    await db_session.flush()

    seller_from_db = await db_session.get(Seller, seller["id"])
    assert seller_from_db is None

    # Проверяем что книги тоже удалились
    books = await db_session.execute(select(Book))
    books = books.scalars().all()

    assert len(books) == 0


# DELETE SELLER WITH WRONG ID
@pytest.mark.asyncio()
async def test_delete_seller_with_wrong_id(db_session, async_client, seller):

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{seller['id'] + 1}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
