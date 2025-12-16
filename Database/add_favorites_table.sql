-- Favorites Tablosu Oluşturma Scripti
-- Bu script, kullanıcıların favori ürünlerini saklamak için Favorites tablosunu oluşturur.

-- Favorites tablosunu oluştur
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Favorites]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[Favorites] (
        [Id] INT IDENTITY(1,1) NOT NULL,
        [UserId] INT NOT NULL,
        [ProductId] INT NOT NULL,
        [CreatedAt] DATETIME NOT NULL DEFAULT GETDATE(),
        CONSTRAINT [PK_Favorites] PRIMARY KEY CLUSTERED ([Id] ASC),
        CONSTRAINT [FK_Favorites_User] FOREIGN KEY ([UserId]) 
            REFERENCES [dbo].[Users] ([Id]) ON DELETE CASCADE,
        CONSTRAINT [FK_Favorites_Product] FOREIGN KEY ([ProductId]) 
            REFERENCES [dbo].[Products] ([Id]) ON DELETE CASCADE,
        CONSTRAINT [UQ_Favorites_UserProduct] UNIQUE ([UserId], [ProductId])
    );
    
    -- Index oluştur (performans için)
    CREATE NONCLUSTERED INDEX [IX_Favorites_UserId] ON [dbo].[Favorites] ([UserId]);
    CREATE NONCLUSTERED INDEX [IX_Favorites_ProductId] ON [dbo].[Favorites] ([ProductId]);
    
    PRINT 'Favorites tablosu başarıyla oluşturuldu.';
END
ELSE
BEGIN
    PRINT 'Favorites tablosu zaten mevcut.';
END
GO


