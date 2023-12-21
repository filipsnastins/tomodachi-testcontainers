# Testing Repositories

- [ ] Test Repository in isolation with a real database.
- [ ] Use fakes/mocks in other unit tests where database access is not required.
- [ ] Test your fake Repository with the same suite of tests as the real Repository.
- [ ] Where it makes sense to use Repository pattern, and where is it an overkill?
- [ ] Round-trip testing to not expose Repository implementation details.

<figure markdown>
  ![Container Diagram - Application with Relational Database](../architecture/c4/level_2_container/01_app_with_relational_db.png)
</figure>

<figure markdown>
  ![Component Diagram - Application with Relational Database](../architecture/c4/level_3_component/01_app_with_relational_db.png)
</figure>

## Ports & Adapters

TODO link to a more general pattern - ports and adapters

## References

- <https://www.cosmicpython.com/book/chapter_02_repository.html>
- <https://martinfowler.com/eaaCatalog/repository.html>
- <https://ddd.mikaelvesavuori.se/tactical-ddd/repositories>
