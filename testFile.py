import pytest
from Car import Car
from CarInventoryNode import CarInventoryNode
from CarInventory import CarInventory

#tests for Car file
def test_car_constructor_and_str():
    car = Car("Nissan", "Altima", 2015, 15000)
    assert str(car) == "Make: NISSAN, Model: ALTIMA, Year: 2015, Price: $15000"

def test_car_gt():
    car1 = Car("Toyota", "Campry", 2010, 12000)
    car2 = Car("Honda", "Accord", 2010, 10000)
    assert car1 > car2

def test_car_lt():
    car1 = Car("Tesla", "Model 3", 2020, 50000)
    car2 = Car("Toyota", "Corolla", 2020, 25000)
    assert car1 < car2

def test_car_eq():
    car1 = Car("Ford", "Escape", 2018, 18000)
    car2 = Car("Ford", "Escape", 2018, 18000)
    assert car1 == car2

def test_car_gt_combination():
    car1 = Car("Tesla", "Model X", 2019, 80000)
    car2 = Car("Tesla", "Model X", 2019, 90000)
    assert car2 > car1

def test_car_lt_combination():
    car1 = Car("Ferrari", "488", 2022, 300000)
    car2 = Car("Ferrari", "488", 2022, 400000)
    assert car1 < car2

def test_car_eq_combination():
    car1 = Car("Chevrolet", "Camaro", 2017, 25000)
    car2 = Car("Chevrolet", "Camaro", 2017, 25000)
    assert car1 == car2

#tests for CarInventoryNode file

def test_car_inventory_node_creation():
    car1 = Car("Toyota", "Camry", 2022, 25000)
    car_node = CarInventoryNode(car1)
    assert car_node.getMake() == "Toyota"
    assert car_node.getModel() == "Camry"
    assert car_node.getParent() is None
    assert car_node.getLeft() is None
    assert car_node.getRight() is None
    assert str(car_node) == "Make: TOYOTA, Model: CAMRY, Year: 2022, Price: $25000\n"

def test_car_inventory_node_parent_and_children():
    car1 = Car("Toyota", "Camry", 2022, 25000)
    car2 = Car("Honda", "Accord", 2020, 22000)
    car3 = Car("Tesla", "Model 3", 2021, 50000)

    car_node1 = CarInventoryNode(car1)
    car_node2 = CarInventoryNode(car2)
    car_node3 = CarInventoryNode(car3)

    car_node1.setLeft(car_node2)
    car_node1.setRight(car_node3)

    assert car_node2.getParent() == car_node1
    assert car_node2.getLeft() is None
    assert car_node2.getRight() is None

    assert car_node3.getParent() == car_node1
    assert car_node3.getLeft() is None
    assert car_node3.getRight() is None

def test_car_inventory_node_str():
    car1 = Car("Toyota", "Camry", 2022, 25000)
    car2 = Car("Honda", "Accord", 2020, 22000)
    car_node = CarInventoryNode(car1)
    car_node.cars.append(car2)

    expected_output = "Make: TOYOTA, Model: CAMRY, Year: 2022, Price: $25000\n" \
                      "Make: HONDA, Model: ACCORD, Year: 2020, Price: $22000\n"

    assert str(car_node) == expected_output

#tests for CarInventory file
def test_carInventory():
    bst = CarInventory()
    
    car1 = Car("Nissan", "Leaf", 2018, 18000)
    car2 = Car("Tesla", "Model3", 2018, 50000)
    car3 = Car("Mercedes", "Sprinter", 2022, 40000)
    car4 = Car("Mercedes", "Sprinter", 2014, 25000)
    car5 = Car("Ford", "Ranger", 2021, 25000)

    bst.addCar(car1)
    bst.addCar(car2)
    bst.addCar(car3)
    bst.addCar(car4)
    bst.addCar(car5)
    assert bst.getBestCar("Nissan", "Leaf") == car1
    assert bst.getBestCar("Mercedes", "Sprinter") == car3
    assert bst.getBestCar("Honda", "Accord") is None

    assert bst.getWorstCar("Nissan", "Leaf") == car1

    assert bst.getWorstCar("Mercedes", "Sprinter") == car4
    assert bst.getBestCar("Honda", "Accord") is None

    assert bst.getTotalInventoryPrice() == 158000


    assert bst.inOrder() == \
"""\
Make: FORD, Model: RANGER, Year: 2021, Price: $25000
Make: MERCEDES, Model: SPRINTER, Year: 2022, Price: $40000
Make: MERCEDES, Model: SPRINTER, Year: 2014, Price: $25000
Make: NISSAN, Model: LEAF, Year: 2018, Price: $18000
Make: TESLA, Model: MODEL3, Year: 2018, Price: $50000
"""


    assert bst.preOrder() == \
"""\
Make: NISSAN, Model: LEAF, Year: 2018, Price: $18000
Make: MERCEDES, Model: SPRINTER, Year: 2022, Price: $40000
Make: MERCEDES, Model: SPRINTER, Year: 2014, Price: $25000
Make: FORD, Model: RANGER, Year: 2021, Price: $25000
Make: TESLA, Model: MODEL3, Year: 2018, Price: $50000
"""

    assert bst.postOrder() == \
"""\
Make: FORD, Model: RANGER, Year: 2021, Price: $25000
Make: MERCEDES, Model: SPRINTER, Year: 2022, Price: $40000
Make: MERCEDES, Model: SPRINTER, Year: 2014, Price: $25000
Make: TESLA, Model: MODEL3, Year: 2018, Price: $50000
Make: NISSAN, Model: LEAF, Year: 2018, Price: $18000
"""





    
