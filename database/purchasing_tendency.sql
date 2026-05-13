
--
-- Database: `purchasing_tendency`
--

-- --------------------------------------------------------

--
-- Table structure for table `admin`
--

CREATE TABLE `admin` (
  `id` int(11) NOT NULL auto_increment,
  `username` varchar(50) default NULL,
  `password` varchar(50) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=2 ;

--
-- Dumping data for table `admin`
--

INSERT INTO `admin` (`id`, `username`, `password`) VALUES
(1, 'admin', 'admin');

-- --------------------------------------------------------

--
-- Table structure for table `buyers`
--

CREATE TABLE `buyers` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(100) default NULL,
  `email` varchar(120) default NULL,
  `mobile` varchar(20) default NULL,
  `location` varchar(150) default NULL,
  `age` int(11) default NULL,
  `gender` varchar(20) default NULL,
  `username` varchar(50) default NULL,
  `password` varchar(100) default NULL,
  `created_at` timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=4 ;

--
-- Dumping data for table `buyers`
--

INSERT INTO `buyers` (`id`, `name`, `email`, `mobile`, `location`, `age`, `gender`, `username`, `password`, `created_at`) VALUES
(1, 'Raj', 'akil@gmail.com', '8148956634', 'Trichy', 22, 'Male', 'raj', '1234', '2026-03-12 11:43:09'),
(2, 'Vijay', 'vijay@gmail.com', '8929090909', 'Chennai', 34, 'Male', 'vijay', '1234', '2026-03-12 12:28:41'),
(3, 'Sam', 'sam@gmail.com', '9876522345', 'Coimbatore', 34, 'Male', 'sam', '1234', '2026-03-12 12:29:22');

-- --------------------------------------------------------

--
-- Table structure for table `cart`
--

CREATE TABLE `cart` (
  `id` int(11) NOT NULL auto_increment,
  `buyer_id` int(11) default NULL,
  `product_id` int(11) default NULL,
  `quantity` int(11) default '1',
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=12 ;

--
-- Dumping data for table `cart`
--

INSERT INTO `cart` (`id`, `buyer_id`, `product_id`, `quantity`) VALUES
(5, 3, 2, 1),
(9, 1, 2, 1);

-- --------------------------------------------------------

--
-- Table structure for table `interactions`
--

CREATE TABLE `interactions` (
  `id` int(11) NOT NULL auto_increment,
  `user_id` int(11) default NULL,
  `product_id` int(11) default NULL,
  `action` varchar(20) default NULL,
  `timestamp` timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=17 ;

--
-- Dumping data for table `interactions`
--

INSERT INTO `interactions` (`id`, `user_id`, `product_id`, `action`, `timestamp`) VALUES
(1, 1, 1, 'cart', '2026-03-12 12:05:14'),
(2, 1, 1, 'purchase', '2026-03-12 12:05:21'),
(3, 1, 2, 'cart', '2026-03-12 12:18:22'),
(4, 1, 2, 'purchase', '2026-03-12 12:18:28'),
(5, 1, 3, 'cart', '2026-03-12 12:18:39'),
(6, 1, 3, 'purchase', '2026-03-12 12:18:45'),
(7, 3, 2, 'cart', '2026-03-12 12:29:38'),
(8, 2, 2, 'cart', '2026-03-12 12:45:14'),
(9, 2, 2, 'purchase', '2026-03-12 12:50:05'),
(10, 1, 3, 'cart', '2026-03-12 15:21:50'),
(11, 1, 3, 'cart', '2026-03-12 16:07:22'),
(12, 1, 3, 'purchase', '2026-03-12 16:07:30'),
(13, 1, 2, 'cart', '2026-03-12 16:07:53'),
(14, 1, 1, 'cart', '2026-03-12 16:08:11'),
(15, 1, 1, 'cart', '2026-03-13 13:25:41'),
(16, 1, 1, 'purchase', '2026-03-13 13:25:51');

-- --------------------------------------------------------

--
-- Table structure for table `orders`
--

CREATE TABLE `orders` (
  `id` int(11) NOT NULL auto_increment,
  `buyer_id` int(11) default NULL,
  `seller_id` int(11) default NULL,
  `product_id` int(11) default NULL,
  `price` float default NULL,
  `status` varchar(20) default 'pending',
  `payment_status` varchar(20) default 'unpaid',
  `created_at` timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=9 ;

--
-- Dumping data for table `orders`
--

INSERT INTO `orders` (`id`, `buyer_id`, `seller_id`, `product_id`, `price`, `status`, `payment_status`, `created_at`) VALUES
(8, 1, 1, 1, 20000, 'approved', 'unpaid', '2026-03-13 13:25:51');

-- --------------------------------------------------------

--
-- Table structure for table `products`
--

CREATE TABLE `products` (
  `id` int(11) NOT NULL auto_increment,
  `seller_id` int(11) default NULL,
  `name` varchar(200) default NULL,
  `price` float default NULL,
  `specification` text,
  `image` varchar(200) default NULL,
  `created_at` timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=7 ;

--
-- Dumping data for table `products`
--

INSERT INTO `products` (`id`, `seller_id`, `name`, `price`, `specification`, `image`, `created_at`) VALUES
(1, 1, 'Oppo Mobile', 20000, 'fyufdktykdkykydcykdcfydcfycf', 'oppo.jpg', '2026-03-12 11:27:22'),
(2, 1, 'MacBook', 170000, 'eowruviiefvi2eihbv efbc vulefv uled qe', 'download.jpg', '2026-03-12 12:12:26'),
(3, 2, 'Nikon Camera', 30000, 'erevjlwrijveiviejicbec', 'nikon.png', '2026-03-12 12:14:35'),
(4, 2, 'Oppo Mobile', 20000, 'dkcnfdgif bwiewcev24', 'oppo.jpg', '2026-03-12 12:15:13'),
(5, 1, 'Headphone', 2000, 'dhifgeiqefnvbenjivb', 'shopping.png', '2026-03-13 13:19:30'),
(6, 1, 'Mobile Case', 200, 'dvby5jmwcrnrjibnrhwhtjnmtnhrbgv', 'images.png', '2026-03-13 13:20:06');

-- --------------------------------------------------------

--
-- Table structure for table `sellers`
--

CREATE TABLE `sellers` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(100) default NULL,
  `email` varchar(100) default NULL,
  `mobile` varchar(20) default NULL,
  `shopname` varchar(100) default NULL,
  `address` text,
  `category` varchar(100) default NULL,
  `latitude` varchar(50) default NULL,
  `longitude` varchar(50) default NULL,
  `username` varchar(50) default NULL,
  `password` varchar(50) default NULL,
  `status` varchar(20) default 'active',
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=3 ;

--
-- Dumping data for table `sellers`
--

INSERT INTO `sellers` (`id`, `name`, `email`, `mobile`, `shopname`, `address`, `category`, `latitude`, `longitude`, `username`, `password`, `status`) VALUES
(1, 'Raj', 'akil@gmail.com', '8148956634', 'D-Mart', '123, Street, trichy', 'Devices', '10.835819416799662', '78.69323016973067', 'raj', '1234', 'active'),
(2, 'Vijay', 'vijay@gmail.com', '8124484080', 'E-Mart', 'Coimbatore', 'Gadgets', '11.006087107065945', '76.96500379427285', 'vijay', '1234', 'active');
