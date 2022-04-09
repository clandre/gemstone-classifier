get_id = function(doc) { return doc._id; }

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
        '$match': {
            'Images': {$gt: 20}
        }
    }
]).map(get_id)