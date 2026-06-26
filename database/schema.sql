-- Disaster Relief Resource Management System
-- ShaktiDB Schema

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('volunteer','ngo','authority','affected')),
    phone TEXT,
    location TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('food','water','medicine','clothing','shelter_item','equipment','other')),
    quantity INTEGER NOT NULL,
    unit TEXT NOT NULL,
    location TEXT NOT NULL,
    status TEXT DEFAULT 'available' CHECK(status IN ('available','allocated','depleted')),
    registered_by INTEGER,
    disaster_type TEXT CHECK(disaster_type IN ('flood','landslide','cyclone','general')),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(registered_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS aid_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requester_id INTEGER NOT NULL,
    resource_type TEXT NOT NULL,
    quantity_needed INTEGER NOT NULL,
    urgency TEXT DEFAULT 'medium' CHECK(urgency IN ('critical','high','medium','low')),
    location TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending','approved','fulfilled','rejected')),
    assigned_resource_id INTEGER,
    reviewed_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(requester_id) REFERENCES users(id),
    FOREIGN KEY(assigned_resource_id) REFERENCES resources(id),
    FOREIGN KEY(reviewed_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS shelters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    location TEXT NOT NULL,
    latitude REAL,
    longitude REAL,
    capacity INTEGER NOT NULL,
    current_occupancy INTEGER DEFAULT 0,
    contact_name TEXT,
    contact_phone TEXT,
    status TEXT DEFAULT 'open' CHECK(status IN ('open','full','closed')),
    facilities TEXT,
    managed_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(managed_by) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS volunteers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    skills TEXT,
    availability TEXT DEFAULT 'available' CHECK(availability IN ('available','assigned','unavailable')),
    assigned_area TEXT,
    assigned_task TEXT,
    emergency_contact TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Seed demo data
INSERT OR IGNORE INTO users (id, name, email, password, role, phone, location) VALUES
(1, 'Admin Authority', 'admin@relief.gov', 'admin123', 'authority', '9000000001', 'Kozhikode HQ'),
(2, 'Red Cross NGO', 'ngo@redcross.org', 'ngo123', 'ngo', '9000000002', 'Kozhikode'),
(3, 'Arjun Volunteer', 'arjun@vol.com', 'vol123', 'volunteer', '9000000003', 'Calicut North'),
(4, 'Meera Affected', 'meera@gmail.com', 'user123', 'affected', '9000000004', 'Flood Zone A');

INSERT OR IGNORE INTO resources (id, name, type, quantity, unit, location, status, registered_by, disaster_type) VALUES
(1, 'Rice Bags', 'food', 200, 'kg', 'Kozhikode Warehouse', 'available', 2, 'flood'),
(2, 'Drinking Water', 'water', 500, 'litres', 'Relief Camp 1', 'available', 3, 'flood'),
(3, 'First Aid Kits', 'medicine', 50, 'kits', 'Medical Center', 'available', 2, 'general'),
(4, 'Life Jackets', 'equipment', 30, 'units', 'Boat Station', 'available', 1, 'flood'),
(5, 'Blankets', 'clothing', 150, 'pieces', 'Relief Camp 2', 'available', 3, 'cyclone');

INSERT OR IGNORE INTO shelters (id, name, location, capacity, current_occupancy, contact_name, contact_phone, status, facilities, managed_by) VALUES
(1, 'Government School Camp', 'Kozhikode North', 300, 120, 'Principal Rajan', '9111111111', 'open', 'Food, Water, Medical', 1),
(2, 'Community Hall Shelter', 'Calicut Beach Area', 150, 148, 'Coordinator Suja', '9222222222', 'full', 'Food, Water', 2),
(3, 'District Sports Complex', 'Kozhikode Central', 500, 210, 'Manager Vinod', '9333333333', 'open', 'Food, Water, Medical, Sanitation', 1);

INSERT OR IGNORE INTO volunteers (user_id, skills, availability, assigned_area, assigned_task, emergency_contact) VALUES
(3, 'First Aid, Boat Operation, Search & Rescue', 'available', 'Flood Zone A', 'Resource Distribution', '9444444444');

INSERT OR IGNORE INTO aid_requests (id, requester_id, resource_type, quantity_needed, urgency, location, description, status) VALUES
(1, 4, 'food', 10, 'critical', 'Flood Zone A, Ward 3', 'Family of 5, no food for 2 days', 'pending'),
(2, 4, 'medicine', 5, 'high', 'Flood Zone A, Ward 3', 'Need medicines for elderly member', 'pending');
