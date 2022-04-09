get_id = function(doc) { return doc._id; }

db.getCollection('gemstone').find({'chemical_formula': {$exists: true}}, {"_id": 1}).map(get_id)