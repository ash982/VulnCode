// DANGEROUS - DO NOT USE
const name = req.body.name;
const query = `MATCH (p:Person) WHERE p.name = "${name}" RETURN p`;
const result = await session.run(query);
