-- ProfileImagePath kolonunu User tablosundan kaldır (eğer varsa)
-- Profil resmi kullanılmıyor, bu kolon gerekli değil

USE WiseCartDB;
GO

-- ProfileImagePath kolonu varsa kaldır
IF EXISTS (
    SELECT * FROM sys.columns 
    WHERE object_id = OBJECT_ID(N'[dbo].[Users]') 
    AND name = 'ProfileImagePath'
)
BEGIN
    ALTER TABLE [dbo].[Users]
    DROP COLUMN ProfileImagePath;
    PRINT 'ProfileImagePath kolonu kaldırıldı.';
END
ELSE
BEGIN
    PRINT 'ProfileImagePath kolonu zaten yok.';
END
GO





