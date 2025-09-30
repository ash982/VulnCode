## unserialize(string $data, array $options = [])
unserialize() takes a single serialized variable and converts it back into a PHP value.

**Warning**
Do not pass untrusted user input to unserialize() **regardless of the options value of allowed_classes**. 
Unserialization can result in code being loaded and executed due to object instantiation and autoloading, 
and a malicious user may be able to exploit this. Use a safe, standard data interchange format such as JSON 
(via `json_decode()` and `json_encode()`) if you need to pass serialized data to the user.
`secure1.php`

If you need to unserialize externally-stored serialized data, consider using `hash_hmac()` for data validation. 
Make sure data is not modified by anyone but you.
`secure2.php`


