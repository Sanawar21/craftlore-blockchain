# Documentation for Craftlore Sawtooth Blockchain and Application Development

This repository contains resources and examples for developing applications on the **Hyperledger Sawtooth** blockchain platform using the **Craftlore** blockchain framework.

Refer to the **`tests`** directory for practical examples and test cases demonstrating the functionality of the application.

Refer to the **`tests/craftlore_client.py`** file for functions that interact with the blockchain.  
This can also be translated to **JavaScript** if needed.

---

## BaseClass Update

An attribute **`additional_info`** has been added to the `BaseClass` to allow for flexible storage of extra information that may not be covered by existing fields.  

- This attribute is a **dictionary** that can hold key-value pairs.  
- It enables applications to store **custom data** as needed.

---

## Models and Classes

Regularly refer to the **`models`** directory for the definitions of various entities used in the application.

The repository consists of two types of entities:

- **Assets**
- **Accounts**

Each entity is represented by a class that inherits from the `BaseClass`.  
The `BaseClass` includes common attributes.

---

## Account Types

There are three types of user accounts:

1. **Supplier**
2. **Artisan**
3. **Buyer**

---

## Common Account Actions

All accounts can perform the following actions on the blockchain:

- **Create a work order**  
  Work orders are requests for products or services that are to be fulfilled by artisans.

- **Transfer assets they own** to another account

- **Delete assets they own**

- **Edit assets they own**

- **Delete their account**

- **Edit their account**

- **Unpack products**  
  When `Product` entities are transferred in a package, they cannot be transferred again without removing the packaging.  
  Therefore, the unpack products function is needed to allow for the individual products to be transferred again.

---

## ArtisanAccount Actions

Additional actions specific to **Artisan accounts**:

- **Create a product batch**  
  A product batch is created automatically when an artisan accepts a work order.  
  The artisan can also create a product batch without a work order to create products on their own.

- **Accept a work order**  
  Means that the artisan agrees to fulfill the request made in the work order.

- **Reject a work order**  
  Means that the artisan declines to fulfill the request made in the work order.

- **Complete a work order**  
  Means that the artisan has fulfilled the request made in the work order.  
  The products for the work order are minted on the blockchain and assigned to the artisan's account.

- **Complete a product batch**  
  Means that the artisan has finished creating the products in the batch.  
  The products are then available for transfer to other accounts.

- **Create a sub assignment**  
  A sub assignment is a task that is part of a larger work order.  
  An artisan can create a sub assignment to delegate part of the work to another artisan.

- **Accept a sub assignment**  
  Means that the artisan agrees to fulfill the task assigned in the sub assignment.

- **Reject a sub assignment**  
  Means that the artisan declines to fulfill the task assigned in the sub assignment.

- **Complete a sub assignment**  
  Means that the artisan has fulfilled the task assigned in the sub assignment.
  No work order or batch can be marked as complete until all sub assignments are marked as complete.

- **Mark a sub assignment as paid**  
  Indicates that the payment for the sub assignment has been made.

- **Add raw material to a batch**  
  Artisans can add raw materials they own to a product batch to keep track of the materials used in the production process.

---

## SupplierAccount Actions

Additional actions specific to **Supplier accounts**:

- **Register a raw material**  
  Suppliers can register raw materials that they can later transfer to artisans.

---

## Admin Accounts

We have introduced **admin accounts** for administrative tasks and oversight.  

At the start of the blockchain, the **`bootstrap`** method is called to create a **Super Admin**.  
The Super Admin can then create other admin accounts.

### Admin Types

1. **Moderator Admin** *(Very powerful)*  
   - Has atomic access to the blockchain state  
   - Can modify any data

2. **Certifier Admin**  
   - Can provide certificates to accounts and assets on the blockchain

3. **Authenticator Admin**  
   - Can authenticate the identity of users  
   - Can verify the truthfulness of the data on the blockchain
