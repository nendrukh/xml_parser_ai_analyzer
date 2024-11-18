from executor import executor


def test_create_task():
    # проверяем создание таски с одним продуктом
    assert executor.run("""<sales_data date="2024-01-01">
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

    # проверяем создание таски с несколькими продуктами
    assert executor.run("""<sales_data date="2024-01-01">
    <products>
        <product>
            <id>1</id>
            <name>Product A</name>
            <quantity>100</quantity>
            <price>1500.00</price>
            <category>Electronics</category>
        </product>
        <product>
            <id>2</id>
            <name>Product B</name>
            <quantity>150</quantity>
            <price>1554.00</price>
            <category>Books</category>
        </product>
    </products>
</sales_data>""")
