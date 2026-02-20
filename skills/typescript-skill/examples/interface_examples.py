#!/usr/bin/env python3
"""TypeScript Skill - 接口生成示例"""

import sys
sys.path.insert(0, '..')

from main import TypeScriptGenerator, InterfaceProperty

def main():
    generator = TypeScriptGenerator()
    
    print("=" * 70)
    print("TypeScript Skill - 接口生成示例")
    print("=" * 70)
    
    # 示例1: 从JSON生成接口
    print("\n1. 从JSON生成接口")
    print("-" * 50)
    
    user_json = {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "profile": {
            "firstName": "John",
            "lastName": "Doe",
            "age": 30
        },
        "roles": ["user", "admin"],
        "isActive": True,
        "lastLogin": None
    }
    
    user_interface = generator.generate_interface("User", user_json)
    print(user_interface)
    
    # 示例2: 从属性列表生成接口
    print("\n2. 从属性列表生成接口")
    print("-" * 50)
    
    product_props = [
        InterfaceProperty("id", "string", readonly=True),
        InterfaceProperty("name", "string"),
        InterfaceProperty("price", "number"),
        InterfaceProperty("description", "string", optional=True),
        InterfaceProperty("inStock", "boolean", default_value="true"),
        InterfaceProperty("categories", "string[]"),
    ]
    
    product_interface = generator.generate_interface("Product", product_props)
    print(product_interface)
    
    # 示例3: 继承接口
    print("\n3. 继承接口")
    print("-" * 50)
    
    admin_data = {
        "permissions": ["read", "write", "delete"],
        "department": "IT"
    }
    
    admin_interface = generator.generate_interface(
        "Admin",
        admin_data,
        extends=["User"],
        description="管理员用户接口"
    )
    print(admin_interface)
    
    # 示例4: API响应接口
    print("\n4. API响应接口")
    print("-" * 50)
    
    api_response = {
        "success": True,
        "data": {"items": [], "total": 0},
        "message": "OK",
        "errors": None
    }
    
    response_interface = generator.generate_interface(
        "ApiResponse",
        api_response,
        generics=["T"]
    )
    print(response_interface)
    
    # 示例5: 复杂嵌套接口
    print("\n5. 复杂嵌套接口")
    print("-" * 50)
    
    order_data = {
        "orderId": "ORD-12345",
        "customer": {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com"
        },
        "items": [
            {
                "productId": "PROD-001",
                "quantity": 2,
                "price": 29.99
            }
        ],
        "shippingAddress": {
            "street": "123 Main St",
            "city": "New York",
            "zipCode": "10001"
        },
        "totalAmount": 59.98,
        "status": "pending"
    }
    
    order_interface = generator.generate_interface("Order", order_data)
    print(order_interface)
    
    # 示例6: React组件Props
    print("\n6. React组件Props")
    print("-" * 50)
    
    button_props = {
        "label": "string",
        "variant": {"type": "'primary' | 'secondary' | 'danger'", "optional": False},
        "size": {"type": "'sm' | 'md' | 'lg'", "optional": True},
        "disabled": {"type": "boolean", "optional": True},
        "onClick": {"type": "(event: React.MouseEvent) => void", "optional": False},
        "icon": {"type": "React.ReactNode", "optional": True}
    }
    
    button_interface = generator.generate_react_props(
        "Button",
        button_props,
        with_children=True
    )
    print(button_interface)
    
    print("\n" + "=" * 70)
    print("示例运行完成!")
    print("=" * 70)


if __name__ == "__main__":
    main()
