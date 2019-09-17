BEGIN TRANSACTION;
DROP TABLE IF EXISTS `statics`;
CREATE TABLE IF NOT EXISTS `statics` (
  `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  `name` TEXT NOT NULL,
  `storage_class` TEXT NOT NULL,
  `type_text` TEXT NOT NULL,
  `filename` TEXT NOT NULL,
  `start_line` INTEGER NOT NULL,
  `start_column` INTEGER NOT NULL,
  `end_line` INTEGER NOT NULL,
  `end_column` INTEGER NOT NULL,
  `mark` TEXT
);
DROP INDEX IF EXISTS `by_type_text`;
CREATE INDEX IF NOT EXISTS `by_type_text` ON `statics` (
  `type_text`
);
DROP INDEX IF EXISTS `by_storage_class`;
CREATE INDEX IF NOT EXISTS `by_storage_class` ON `statics` (
  `storage_class`
);
DROP INDEX IF EXISTS `by_name`;
CREATE INDEX IF NOT EXISTS `by_name` ON `statics` (
  `name`
);
DROP INDEX IF EXISTS `by_mark`;
CREATE INDEX IF NOT EXISTS `by_mark` ON `statics` (
  `mark`
);
DROP INDEX IF EXISTS `by_filename`;
CREATE INDEX IF NOT EXISTS `by_filename` ON `statics` (
  `filename`
);
COMMIT;
