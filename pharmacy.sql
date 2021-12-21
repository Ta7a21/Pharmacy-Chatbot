-- phpMyAdmin SQL Dump
-- version 4.9.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Dec 21, 2021 at 12:03 AM
-- Server version: 8.0.18
-- PHP Version: 7.3.11

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `pharmacy`
--

-- --------------------------------------------------------

--
-- Table structure for table `clients`
--

CREATE TABLE `clients` (
  `phoneNumber` varchar(15) COLLATE utf8mb4_general_ci NOT NULL,
  `address` varchar(80) COLLATE utf8mb4_general_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `clients`
--

INSERT INTO `clients` (`phoneNumber`, `address`) VALUES
('111', 'mohamed');

-- --------------------------------------------------------

--
-- Table structure for table `medicines`
--

CREATE TABLE `medicines` (
  `Id` int(11) NOT NULL,
  `Name` varchar(80) COLLATE utf8mb4_general_ci NOT NULL,
  `Price` int(11) NOT NULL,
  `Amount` int(11) NOT NULL,
  `Category` varchar(80) COLLATE utf8mb4_general_ci NOT NULL,
  `Disease` varchar(80) COLLATE utf8mb4_general_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `medicines`
--

INSERT INTO `medicines` (`Id`, `Name`, `Price`, `Amount`, `Category`, `Disease`) VALUES
(1, 'Antinal', 12, 50, 'Medicines', 'Diarrhea '),
(2, 'Panadol', 40, 22, 'Medicines', 'Cold'),
(3, 'Shampoo Clear', 45, 33, 'Hair Care', ''),
(4, 'Cataflam', 13, 44, 'Medicines', 'Pain Killer'),
(5, 'Fresh Active Deodorant Spray', 46, 90, 'Personal Care', ''),
(6, 'Dove Shower Gel', 50, 17, 'Personal Care', ''),
(7, 'Dettol Skin Care Soap', 9, 14, 'Skin Care', '');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `clients`
--
ALTER TABLE `clients`
  ADD UNIQUE KEY `phoneNumber` (`phoneNumber`);

--
-- Indexes for table `medicines`
--
ALTER TABLE `medicines`
  ADD PRIMARY KEY (`Id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `medicines`
--
ALTER TABLE `medicines`
  MODIFY `Id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
