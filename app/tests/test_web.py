from fastapi.testclient import TestClient

from web_app import app

client = TestClient(app)


def test_schedule_task():
    # проверяем отправку валидного запроса
    response = client.post("/schedule_task", content="""<sales_data date="2024-01-01">
    <products>
        <product>
            <id>1</id>
            <name>Product A</name>
            <quantity>100</quantity>
            <price>1500.00</price>
            <category>Electronics</category>
        </product>
    </products>
</sales_data>""")
    assert response.status_code == 200

    task_id = response.json()["task_id"]
    assert response.json() == {"status": "Task scheduled", "task_id": task_id}
