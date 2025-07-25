CREATE TABLE Albums (
    SingerId INT64 NOT NULL,
    AlbumId INT64 NOT NULL,
    AlbumTitle STRING(MAX)
) PRIMARY KEY(SingerId, AlbumId);

INSERT INTO Albums (SingerId, AlbumId, AlbumTitle) VALUES
    (1, 1, 'My First Album'),
    (1, 2, 'My Second Album'),
    (2, 3, 'Another Album');
