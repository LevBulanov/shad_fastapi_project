import pytest
from fastapi import status
from sqlalchemy import select

from src.models.books import Book
from src.models.seller import Seller

API_V1_URL_PREFIX = "/api/v1/books"


# CREATE BOOK
@pytest.mark.asyncio()
async def test_create_book(async_client, auth_headers):
    data = {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "count_pages": 300,
        "year": 2025,
    }

    response = await async_client.post(
        f"{API_V1_URL_PREFIX}/",
        json=data,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    resp_book_id = result_data.pop("id", None)
    seller_id = result_data.pop("seller_id", None)

    assert resp_book_id is not None
    assert seller_id is not None

    assert result_data == {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "pages": 300,
        "year": 2025,
    }


@pytest.mark.asyncio()
async def test_create_book_with_old_year(async_client, auth_headers):
    data = {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "count_pages": 300,
        "year": 1986,
    }

    response = await async_client.post(
        f"{API_V1_URL_PREFIX}/",
        json=data,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# GET BOOKS
@pytest.mark.asyncio()
async def test_get_books(db_session, async_client, seller):
    book = Book(
        author="Pushkin",
        title="Eugeny Onegin",
        year=2021,
        pages=104,
        seller_id=seller["id"],
    )

    book_2 = Book(
        author="Lermontov",
        title="Mziri",
        year=2021,
        pages=108,
        seller_id=seller["id"],
    )

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["books"]) == 2

    assert response.json() == {
        "books": [
            {
                "title": "Eugeny Onegin",
                "author": "Pushkin",
                "year": 2021,
                "id": book.id,
                "pages": 104,
                "seller_id": seller["id"],
            },
            {
                "title": "Mziri",
                "author": "Lermontov",
                "year": 2021,
                "id": book_2.id,
                "pages": 108,
                "seller_id": seller["id"],
            },
        ]
    }


# GET SINGLE BOOK
@pytest.mark.asyncio()
async def test_get_single_book(db_session, async_client, seller):
    book = Book(
        author="Pushkin",
        title="Eugeny Onegin",
        year=2001,
        pages=104,
        seller_id=seller["id"],
    )

    book_2 = Book(
        author="Lermontov",
        title="Mziri",
        year=1997,
        pages=104,
        seller_id=seller["id"],
    )

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/{book.id}")

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {
        "title": "Eugeny Onegin",
        "author": "Pushkin",
        "year": 2001,
        "pages": 104,
        "id": book.id,
        "seller_id": seller["id"],
    }


@pytest.mark.asyncio()
async def test_get_single_book_with_wrong_id(db_session, async_client, seller):
    book = Book(
        author="Pushkin",
        title="Eugeny Onegin",
        year=2001,
        pages=104,
        seller_id=seller["id"],
    )

    db_session.add(book)
    await db_session.flush()

    response = await async_client.get(f"{API_V1_URL_PREFIX}/426548")

    assert response.status_code == status.HTTP_404_NOT_FOUND


# UPDATE BOOK
@pytest.mark.asyncio()
async def test_update_book(db_session, async_client, seller, auth_headers):
    book = Book(
        author="Pushkin",
        title="Eugeny Onegin",
        year=2001,
        pages=104,
        seller_id=seller["id"],
    )

    db_session.add(book)
    await db_session.flush()

    data = {
        "title": "Mziri",
        "author": "Lermontov",
        "pages": 250,
        "year": 2024,
        "id": book.id,
        "seller_id": seller["id"],
    }

    response = await async_client.put(
        f"{API_V1_URL_PREFIX}/{book.id}",
        json=data,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_200_OK

    await db_session.flush()

    res = await db_session.get(Book, book.id)

    assert res.title == "Mziri"
    assert res.author == "Lermontov"
    assert res.pages == 250
    assert res.year == 2024
    assert res.id == book.id


# DELETE BOOK
@pytest.mark.asyncio()
async def test_delete_book(db_session, async_client, seller):
    book = Book(
        author="Lermontov",
        title="Mtziri",
        pages=510,
        year=2024,
        seller_id=seller["id"],
    )

    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{book.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    await db_session.flush()

    all_books = await db_session.execute(select(Book))
    res = all_books.scalars().all()

    assert len(res) == 0


@pytest.mark.asyncio()
async def test_delete_book_with_invalid_book_id(db_session, async_client, seller):
    book = Book(
        author="Lermontov",
        title="Mtziri",
        pages=510,
        year=2024,
        seller_id=seller["id"],
    )

    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"{API_V1_URL_PREFIX}/{book.id + 1}")

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio()
async def test_update_book_forbidden(db_session, async_client, seller, auth_headers):
    # создаем другого продавца (владельца книги)
    other_seller = Seller(
        first_name="Other",
        last_name="Seller",
        email="other@test.com",
        password="hashed",
    )

    db_session.add(other_seller)
    await db_session.flush()

    # книга принадлежит другому продавцу
    book = Book(
        author="Pushkin",
        title="Eugeny Onegin",
        year=2001,
        pages=104,
        seller_id=other_seller.id,
    )

    db_session.add(book)
    await db_session.flush()

    data = {
        "title": "New Title",
        "author": "Someone",
        "pages": 200,
        "year": 2024,
        "id": book.id,
        "seller_id": other_seller.id,
    }

    response = await async_client.put(
        f"{API_V1_URL_PREFIX}/{book.id}",
        json=data,
        headers=auth_headers,  # токен текущего seller
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
