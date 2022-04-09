db.getCollection('gemstone').aggregate([
    {
        '$match': {
            'chemical_formula': {
                '$exists': true
            }
        }
    }, {
        '$project': {
            'Images': {
                '$size': '$Images'
            }
        }
    }, {
        '$group': {
            '_id': null,
            'count': {
                '$sum': '$Images'
            }
        }
    }
])