import streamlit as st
import pandas as pd

# Initialize session state for inventory if it doesn't exist
if 'stationery_inventory' not in st.session_state:
    st.session_state.stationery_inventory = {}

# Predefined categories
CATEGORIES = [
    "Writing Instruments",
    "Paper Products",
    "Correction Tools",
    "Geometry Tools",
    "Files & Folders",
    "Office Supplies",
    "Art & Craft",
    "School Essentials"
]

def add_item():
    st.subheader("Add New Stationery Item")
    with st.form("add_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Item Name").strip().title()
            category = st.selectbox("Category", CATEGORIES)
            publisher = st.text_input("Publisher/Brand").strip().title()
        with col2:
            quantity = st.number_input("Quantity in Stock", min_value=0, step=1)
            price = st.number_input("Price (₹)", min_value=0.0, format="%.2f")
            min_stock = st.number_input("Minimum Stock Level", min_value=0, step=1, value=5)
        
        submitted = st.form_submit_button("Add Item")
        if submitted:
            if name:
                if name in st.session_state.stationery_inventory:
                    st.session_state.stationery_inventory[name]["quantity"] += quantity
                    st.success(f"Quantity updated for '{name}'!")
                else:
                    st.session_state.stationery_inventory[name] = {
                        "category": category,
                        "quantity": quantity,
                        "publisher": publisher,
                        "price": price,
                        "min_stock": min_stock
                    }
                    st.success(f"'{name}' added successfully!")
                
                # Check stock balance after adding/updating
                check_stock_balance(name)
            else:
                st.error("Please enter an item name")

def view_inventory():
    st.subheader("Stationery Inventory")
    
    if not st.session_state.stationery_inventory:
        st.info("No items in stock.")
    else:
        # Convert to DataFrame for nice display
        df = pd.DataFrame.from_dict(st.session_state.stationery_inventory, orient='index')
        df.index.name = 'Name'
        df.reset_index(inplace=True)
        df = df[['Name', 'category', 'publisher', 'price', 'quantity', 'min_stock']]
        
        # Add stock status column
        df['Status'] = df.apply(
            lambda row: "🟢 Adequate" if row['quantity'] >= row['min_stock'] else "🔴 Low Stock", 
            axis=1
        )
        
        df.columns = ['Name', 'Category', 'Brand', 'Price (₹)', 'Quantity', 'Min Stock', 'Status']
        
        # Add filtering options
        st.sidebar.subheader("Filter Inventory")
        filter_category = st.sidebar.selectbox(
            "Filter by Category", 
            ["All"] + sorted(list(df['Category'].unique()))
        )
        filter_status = st.sidebar.selectbox(
            "Filter by Stock Status", 
            ["All", "Adequate", "Low Stock"]
        )
        
        # Apply filters
        if filter_category != "All":
            df = df[df['Category'] == filter_category]
        if filter_status != "All":
            status_filter = filter_status == "Adequate"
            df = df[df['Status'].str.contains("🟢" if status_filter else "🔴")]
        
        st.dataframe(
            df.style.apply(
                lambda x: ['background-color: #ffcccc' if x['Status'] == '🔴 Low Stock' else '' for i, x in df.iterrows()], 
                axis=1
            ),
            hide_index=True,
            use_container_width=True
        )
        
        # Show statistics
        total_items = len(df)
        total_quantity = df['Quantity'].sum()
        total_value = (df['Price (₹)'] * df['Quantity']).sum()
        low_stock_items = len(df[df['Status'] == '🔴 Low Stock'])
        
        st.subheader("Inventory Summary")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Items", total_items)
        col2.metric("Total Quantity", total_quantity)
        col3.metric("Total Value", f"₹{total_value:,.2f}")
        col4.metric("Low Stock Items", low_stock_items, delta_color="inverse")

def check_stock_balance(item_name=None):
    """Check and alert for low stock items"""
    if not st.session_state.stationery_inventory:
        return
    
    low_stock_items = []
    
    if item_name:  # Check single item
        item = st.session_state.stationery_inventory[item_name]
        if item['quantity'] < item['min_stock']:
            st.warning(f"⚠️ Low stock alert for {item_name}! Current: {item['quantity']}, Minimum: {item['min_stock']}")
    else:  # Check all items
        for name, details in st.session_state.stationery_inventory.items():
            if details['quantity'] < details['min_stock']:
                low_stock_items.append(name)
        
        if low_stock_items:
            with st.sidebar:
                st.error("⚠️ Low Stock Alert!")
                for item in low_stock_items:
                    st.write(f"- {item}")

def search_item():
    st.subheader("Search Item")
    search_term = st.text_input("Enter item name to search").strip().title()
    
    if search_term:
        if search_term in st.session_state.stationery_inventory:
            item = st.session_state.stationery_inventory[search_term]
            st.success("Item found!")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Name:** {search_term}")
                st.markdown(f"**Category:** {item['category']}")
                st.markdown(f"**Brand:** {item['publisher']}")
            with col2:
                st.markdown(f"**Price:** ₹{item['price']:.2f}")
                st.markdown(f"**Quantity in Stock:** {item['quantity']}")
                st.markdown(f"**Minimum Stock Level:** {item['min_stock']}")
            
            # Show stock status
            if item['quantity'] < item['min_stock']:
                st.error(f"⚠️ Low stock! Current: {item['quantity']}, Minimum: {item['min_stock']}")
            else:
                st.success(f"Stock level adequate ({item['quantity']})")
        else:
            st.error("Item not found!")

def update_item():
    st.subheader("Update Item")
    item_names = list(st.session_state.stationery_inventory.keys())
    
    if not item_names:
        st.warning("No items in inventory to update")
        return
    
    selected_item = st.selectbox("Select item to update", item_names)
    
    if selected_item:
        item = st.session_state.stationery_inventory[selected_item]
        
        with st.form("update_form"):
            st.markdown(f"**Current Details for {selected_item}**")
            
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Name", value=selected_item).strip().title()
                new_category = st.selectbox(
                    "Category", 
                    CATEGORIES, 
                    index=CATEGORIES.index(item['category'])
                )
                new_publisher = st.text_input("Publisher/Brand", value=item['publisher'])
            with col2:
                new_price = st.number_input(
                    "Price (₹)", 
                    value=float(item['price']), 
                    min_value=0.0, 
                    format="%.2f"
                )
                new_quantity = st.number_input(
                    "Quantity", 
                    value=item['quantity'], 
                    min_value=0, 
                    step=1
                )
                new_min_stock = st.number_input(
                    "Minimum Stock Level", 
                    value=item['min_stock'], 
                    min_value=0, 
                    step=1
                )
            
            submitted = st.form_submit_button("Update Item")
            if submitted:
                # Handle name change
                if new_name != selected_item:
                    st.session_state.stationery_inventory[new_name] = st.session_state.stationery_inventory.pop(selected_item)
                    selected_item = new_name
                
                # Update all fields
                st.session_state.stationery_inventory[selected_item] = {
                    "category": new_category,
                    "publisher": new_publisher,
                    "price": new_price,
                    "quantity": new_quantity,
                    "min_stock": new_min_stock
                }
                st.success(f"'{selected_item}' updated successfully!")
                
                # Check stock balance after update
                check_stock_balance(selected_item)

def main():
    st.set_page_config(
        page_title="Stationery Shop Inventory", 
        page_icon="📚", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.title("📚 Stationery Shop Inventory System")
    
    menu_options = {
        "Add New Item": add_item,
        "View Inventory": view_inventory,
        "Search Item": search_item,
        "Update Item": update_item
    }
    
    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        selected_option = st.radio("Select an option", list(menu_options.keys()))
        
        st.divider()
        st.header("Inventory Summary")
        if st.session_state.stationery_inventory:
            total_items = len(st.session_state.stationery_inventory)
            total_qty = sum(item['quantity'] for item in st.session_state.stationery_inventory.values())
            total_value = sum(item['price'] * item['quantity'] for item in st.session_state.stationery_inventory.values())
            
            st.markdown(f"**Total Items:** {total_items}")
            st.markdown(f"**Total Quantity:** {total_qty}")
            st.markdown(f"**Total Value:** ₹{total_value:,.2f}")
            
            # Check stock balance for all items
            check_stock_balance()
        else:
            st.info("No items in inventory")
    
    # Display the selected page
    menu_options[selected_option]()

if __name__ == "__main__":
    main()