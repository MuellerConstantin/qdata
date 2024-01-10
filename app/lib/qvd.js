const {QvdFile, QvdSymbol} = require('qvd4js');

/**
 * Utility class for deserializing QVD files.
 */
class QvdFileDeserializer {
  /**
   * Deserializes a QVD file.
   *
   * @param {object} object The object to deserialize.
   * @return {QvdFile} The deserialized QVD file.
   */
  static deserialize(object) {
    const _symbolTable = object._symbolTable.map((column) =>
      column.map((value) => new QvdSymbol(value._intValue, value._doubleValue, value._stringValue)),
    );

    return new QvdFile(object._path, object._header, _symbolTable, object._indexTable);
  }
}

module.exports = {QvdFileDeserializer};
