-- CINEBOOK Database Schema
-- SQLite database for the CINEBOOK reference project.
-- This file is executed once (by init_db.py) to create empty tables.

-- ==========================================================
-- Table: movies
-- Stores the basic catalog of movies shown in the cinema.
-- ==========================================================
CREATE TABLE IF NOT EXISTS movies (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    genre       TEXT NOT NULL,
    language    TEXT NOT NULL,
    duration    INTEGER NOT NULL,      -- duration in minutes
    rating      TEXT NOT NULL,         -- e.g. "PG-13", "U/A", "7.8/10"
    description TEXT NOT NULL,
    poster_color TEXT NOT NULL DEFAULT '#4b5563'  -- used for the placeholder poster (no real images used)
);

-- ==========================================================
-- Table: theatres
-- Stores each cinema screen/hall.
-- ==========================================================
CREATE TABLE IF NOT EXISTS theatres (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    name     TEXT NOT NULL,            -- e.g. "Screen 1"
    location TEXT NOT NULL             -- e.g. "CineBook Downtown"
);

-- ==========================================================
-- Table: shows
-- Each row is one screening: a specific movie, at a specific
-- theatre, on a specific date and time.
-- ==========================================================
CREATE TABLE IF NOT EXISTS shows (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    movie_id    INTEGER NOT NULL,
    theatre_id  INTEGER NOT NULL,
    show_date   TEXT NOT NULL,         -- format: YYYY-MM-DD
    show_time   TEXT NOT NULL,         -- format: HH:MM (24hr)
    price       REAL NOT NULL DEFAULT 200.0,   -- price per seat (sample currency unit)
    FOREIGN KEY (movie_id)   REFERENCES movies(id),
    FOREIGN KEY (theatre_id) REFERENCES theatres(id)
);

-- ==========================================================
-- Table: seats
-- Each row is ONE seat for ONE show. Seats are generated
-- per-show so that the same physical seat number can be
-- free in one show and booked in another.
-- ==========================================================
CREATE TABLE IF NOT EXISTS seats (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    show_id    INTEGER NOT NULL,
    seat_label TEXT NOT NULL,          -- e.g. "A1", "B5"
    is_booked  INTEGER NOT NULL DEFAULT 0,  -- 0 = free, 1 = booked
    FOREIGN KEY (show_id) REFERENCES shows(id)
);

-- ==========================================================
-- Table: bookings
-- One row per completed (simulated) booking.
-- ==========================================================
CREATE TABLE IF NOT EXISTS bookings (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    show_id       INTEGER NOT NULL,
    customer_name TEXT NOT NULL,
    num_seats     INTEGER NOT NULL,
    total_amount  REAL NOT NULL,
    created_at    TEXT NOT NULL,       -- timestamp string
    FOREIGN KEY (show_id) REFERENCES shows(id)
);

-- ==========================================================
-- Table: booking_seats
-- Junction table: which seats belong to which booking.
-- A booking can contain many seats; a seat belongs to one booking.
-- ==========================================================
CREATE TABLE IF NOT EXISTS booking_seats (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL,
    seat_id    INTEGER NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES bookings(id),
    FOREIGN KEY (seat_id)    REFERENCES seats(id)
);
